import numpy as np


def _turn_taking_speakers(segments):
    if not segments:
        return []

    def is_question(txt):
        t = (txt or "").strip()
        if not t:
            return False
        if t.endswith("?"):
            return True
        starters = (
            "what ",
            "why ",
            "how ",
            "when ",
            "where ",
            "who ",
            "can ",
            "do ",
            "did ",
            "are ",
            "is ",
            "will ",
            "would ",
            "could ",
            "should ",
        )
        t2 = t.lower()
        return t2.startswith(starters)

    def looks_like_answer(txt):
        t = (txt or "").strip().lower()
        if not t:
            return False
        answer_starters = (
            "yes",
            "no",
            "yeah",
            "yep",
            "nope",
            "i ",
            "i'm ",
            "my ",
            "because",
            "it is ",
            "today is ",
        )
        return t.startswith(answer_starters)

    speakers = np.ones(len(segments), dtype=int)
    last_end = None
    cur = 1
    prev_was_question = False
    for i, s in enumerate(segments):
        start = float(s.get("start", 0.0))
        gap = (start - last_end) if last_end is not None else 0.0
        txt = (s.get("text") or "").strip()

        if gap >= 0.8:
            cur = 2 if cur == 1 else 1
        else:
            if prev_was_question and looks_like_answer(txt):
                cur = 2 if cur == 1 else 1
            elif is_question(txt) and i > 0:
                if looks_like_answer((segments[i - 1].get("text") or "")):
                    cur = 2 if cur == 1 else 1

        speakers[i] = cur
        prev_was_question = is_question(txt)
        last_end = float(s.get("end", start))

    out = []
    for i, s in enumerate(segments):
        s2 = dict(s)
        s2["speaker"] = int(speakers[i])
        out.append(s2)
    return out


def diarize_segments(audio_path, segments, n_speakers=2):
    if not segments:
        return []

    try:
        import librosa
        from sklearn.cluster import KMeans
    except Exception as e:
        print(f"Diarization dependency issue: {e}")
        return _turn_taking_speakers(segments)

    try:
        y, sr = librosa.load(audio_path, sr=16000, mono=True)
    except Exception as e:
        print(f"Audio load error: {e}")
        return [{**s, "speaker": 1} for s in segments]

    feats = []
    valid_idx = []

    min_dur_s = 1.0
    hop_length = 160
    fmin = 50
    fmax = 400

    for i, s in enumerate(segments):
        start = float(s.get("start", 0.0))
        end = float(s.get("end", start))
        if end <= start:
            continue

        mid = 0.5 * (start + end)
        win_a = mid - 0.5 * max(min_dur_s, (end - start))
        win_b = mid + 0.5 * max(min_dur_s, (end - start))
        a = int(max(0, win_a * sr))
        b = int(min(len(y), win_b * sr))
        if b - a < int(0.25 * sr):
            continue

        seg = y[a:b]
        try:
            mfcc = librosa.feature.mfcc(y=seg, sr=sr, n_mfcc=13)

            rms = librosa.feature.rms(y=seg, hop_length=hop_length)
            rms_mean = float(np.mean(rms)) if rms.size else 0.0
            rms_std = float(np.std(rms)) if rms.size else 0.0

            f0, _, _ = librosa.pyin(seg, fmin=fmin, fmax=fmax, sr=sr, hop_length=hop_length)
            if f0 is None:
                f0 = np.array([])
            f0_valid = f0[np.isfinite(f0)] if f0.size else np.array([])
            f0_mean = float(np.mean(f0_valid)) if f0_valid.size else 0.0
            f0_std = float(np.std(f0_valid)) if f0_valid.size else 0.0

            v = np.concatenate(
                [mfcc.mean(axis=1), mfcc.std(axis=1), np.array([rms_mean, rms_std, f0_mean, f0_std])],
                axis=0,
            )
            feats.append(v)
            valid_idx.append(i)
        except Exception:
            continue

    speakers = np.ones(len(segments), dtype=int)

    if len(feats) >= 2:
        X = np.stack(feats, axis=0)
        k = min(int(n_speakers), X.shape[0])
        try:
            labels = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(X)
            for idx, lab in zip(valid_idx, labels):
                speakers[idx] = int(lab) + 1
        except Exception as e:
            print(f"Diarization clustering error: {e}")

    unique = set(int(speakers[i]) for i in valid_idx) if valid_idx else {1}
    if len(unique) < 2 and len(segments) >= 2:
        return _turn_taking_speakers(segments)

    out = []
    for i, s in enumerate(segments):
        s2 = dict(s)
        s2["speaker"] = int(speakers[i])
        out.append(s2)
    return out


def format_diarized_transcript(segments_with_speakers, speaker_prefix="Person"):
    segs = segments_with_speakers or []
    if not segs:
        return ""

    speakers = [int(s.get("speaker", 1)) for s in segs]
    unique = set(speakers)

    if len(unique) <= 1:
        parts = []
        for s in segs:
            txt = (s.get("text") or "").strip()
            if txt:
                parts.append(txt)
        return " ".join(parts).strip()

    merged = []
    cur_spk = None
    cur_txt = []
    for s in segs:
        spk = int(s.get("speaker", 1))
        txt = (s.get("text") or "").strip()
        if not txt:
            continue
        if cur_spk is None:
            cur_spk = spk
            cur_txt = [txt]
            continue
        if spk == cur_spk:
            cur_txt.append(txt)
        else:
            merged.append((cur_spk, " ".join(cur_txt).strip()))
            cur_spk = spk
            cur_txt = [txt]

    if cur_spk is not None and cur_txt:
        merged.append((cur_spk, " ".join(cur_txt).strip()))

    lines = [f"{speaker_prefix} {spk}: {txt}" for spk, txt in merged if txt]
    return "\n".join(lines).strip()
