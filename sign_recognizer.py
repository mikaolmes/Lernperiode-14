"""
ASL Sign Language Letter Recognizer
====================================
Recognizes ASL alphabet letters (A-Y) from MediaPipe hand landmarks.
Letters J and Z require motion and cannot be detected from a single frame.
"""


class SignLanguageRecognizer:
    # Landmark indices
    WRIST = 0
    THUMB_CMC, THUMB_MCP, THUMB_IP, THUMB_TIP = 1, 2, 3, 4
    INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP = 5, 6, 7, 8
    MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP = 9, 10, 11, 12
    RING_MCP, RING_PIP, RING_DIP, RING_TIP = 13, 14, 15, 16
    PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP = 17, 18, 19, 20

    def _dist(self, lm, i, j):
        return ((lm[i].x - lm[j].x) ** 2 + (lm[i].y - lm[j].y) ** 2) ** 0.5

    def _hand_size(self, lm):
        return self._dist(lm, self.WRIST, self.MIDDLE_MCP)

    def _is_extended(self, lm, tip, pip):
        return lm[tip].y < lm[pip].y

    def _is_curled(self, lm, tip, mcp):
        return lm[tip].y > lm[mcp].y

    def _thumb_extended(self, lm, handedness):
        if handedness == "Right":
            return lm[self.THUMB_TIP].x > lm[self.THUMB_IP].x
        return lm[self.THUMB_TIP].x < lm[self.THUMB_IP].x

    def _is_pointing_sideways(self, lm, tip, mcp):
        return abs(lm[tip].x - lm[mcp].x) > abs(lm[tip].y - lm[mcp].y)

    def recognize(self, lm, handedness="Right"):
        """
        Recognize an ASL letter from hand landmarks.

        Args:
            lm: List of 21 MediaPipe hand landmarks
            handedness: "Left" or "Right"

        Returns:
            str: Recognized letter or "?"
        """
        thumb = self._thumb_extended(lm, handedness)
        index = self._is_extended(lm, 8, 6)
        middle = self._is_extended(lm, 12, 10)
        ring = self._is_extended(lm, 16, 14)
        pinky = self._is_extended(lm, 20, 18)

        n_up = sum([index, middle, ring, pinky])
        hs = self._hand_size(lm)
        if hs == 0:
            return "?"

        # Normalized distances between key points
        thumb_index = self._dist(lm, 4, 8) / hs
        index_middle = self._dist(lm, 8, 12) / hs
        middle_ring = self._dist(lm, 12, 16) / hs

        # Is index/middle pointing sideways?
        idx_sideways = self._is_pointing_sideways(lm, 8, 5)
        mid_sideways = self._is_pointing_sideways(lm, 12, 9)

        # --- Y: thumb + pinky out, index/middle/ring down ---
        if thumb and pinky and not index and not middle and not ring:
            return "Y"

        # --- I: only pinky up, thumb folded ---
        if not thumb and pinky and not index and not middle and not ring:
            return "I"

        # --- L: thumb + index out, others down ---
        if thumb and index and not middle and not ring and not pinky:
            if not idx_sideways:
                return "L"

        # --- G: index pointing sideways, others down ---
        if idx_sideways and not middle and not ring and not pinky:
            if index or (lm[8].y < lm[5].y):
                return "G"

        # --- H: index + middle pointing sideways, others down ---
        if idx_sideways and mid_sideways and not ring and not pinky:
            return "H"

        # --- D: index up, thumb touching middle finger ---
        if index and not middle and not ring and not pinky:
            if self._dist(lm, 4, 12) / hs < 0.4:
                return "D"

        # --- X: index hooked (tip between PIP and MCP), others down ---
        if not middle and not ring and not pinky and not thumb:
            if lm[8].y > lm[6].y and lm[8].y < lm[5].y:
                return "X"

        # --- V: index + middle up and spread, others down ---
        if index and middle and not ring and not pinky:
            if index_middle > 0.25:
                if not thumb:
                    return "V"
                else:
                    return "K"

        # --- R: index + middle up and crossed ---
        if index and middle and not ring and not pinky and not thumb:
            if abs(lm[8].x - lm[12].x) < 0.02:
                return "R"

        # --- U: index + middle up and together ---
        if index and middle and not ring and not pinky and not thumb:
            return "U"

        # --- W: index + middle + ring up, pinky down ---
        if index and middle and ring and not pinky:
            return "W"

        # --- F: thumb-index pinch + middle/ring/pinky up ---
        if middle and ring and pinky and thumb_index < 0.15:
            return "F"

        # --- B: all 4 fingers up, thumb folded ---
        if index and middle and ring and pinky:
            return "B"

        # --- O: all fingers curved toward thumb (tips close to thumb tip) ---
        if n_up == 0 and not thumb:
            if thumb_index < 0.15:
                return "O"

        # --- C: curved hand, partially open ---
        if n_up == 0 and thumb:
            if thumb_index > 0.25:
                return "C"

        # --- E: all fingers curled, thumb across ---
        if n_up == 0 and not thumb:
            if thumb_index > 0.1:
                return "E"

        # --- A vs S: fist ---
        if n_up == 0:
            if thumb:
                return "A"
            return "S"

        return "?"

    def recognize_from_result(self, detection_result):
        """
        Recognize letters from a full MediaPipe detection result.

        Args:
            detection_result: MediaPipe HandLandmarkerResult

        Returns:
            list of str: Recognized letter for each detected hand
        """
        if not detection_result.hand_landmarks:
            return []

        results = []
        for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
            handedness = "Right"
            if detection_result.handedness:
                handedness = detection_result.handedness[idx][0].category_name

            letter = self.recognize(hand_landmarks, handedness)
            results.append(letter)

        return results
