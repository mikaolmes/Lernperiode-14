"""
ASL Sign Language Letter Recognizer
====================================
Recognizes ASL alphabet letters (A-Y) from MediaPipe hand landmarks.
Letters J and Z require motion and cannot be detected from a single frame.
Improved with angle-invariant geometric calculations for better multi-angle detection.
"""


class SignLanguageRecognizer:
    # Landmark indices
    WRIST = 0
    THUMB_CMC, THUMB_MCP, THUMB_IP, THUMB_TIP = 1, 2, 3, 4
    INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP = 5, 6, 7, 8
    MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP = 9, 10, 11, 12
    RING_MCP, RING_PIP, RING_DIP, RING_TIP = 13, 14, 15, 16
    PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP = 17, 18, 19, 20

    def _dist_3d(self, lm, i, j):
        """Calculate 3D distance (includes depth from z-coordinate)"""
        return ((lm[i].x - lm[j].x) ** 2 + (lm[i].y - lm[j].y) ** 2 + (lm[i].z - lm[j].z) ** 2) ** 0.5

    def _dist(self, lm, i, j):
        """Calculate 2D distance (ignoring depth)"""
        return ((lm[i].x - lm[j].x) ** 2 + (lm[i].y - lm[j].y) ** 2) ** 0.5

    def _hand_size(self, lm):
        """Calculate hand size using 3D distance for better angle invariance"""
        return self._dist_3d(lm, self.WRIST, self.MIDDLE_MCP)

    def _is_extended(self, lm, tip, pip, threshold=0.0):
        """Check if a finger is extended (tip above PIP joint in y-axis)"""
        return lm[tip].y < lm[pip].y - threshold

    def _is_curled(self, lm, tip, mcp):
        """Check if a finger is curled (tip below MCP joint)"""
        return lm[tip].y > lm[mcp].y

    def _thumb_extended(self, lm, handedness):
        """Check if thumb is extended, accounting for left/right hand"""
        if handedness == "Right":
            return lm[self.THUMB_TIP].x > lm[self.THUMB_IP].x
        return lm[self.THUMB_TIP].x < lm[self.THUMB_IP].x

    def _is_pointing_sideways(self, lm, tip, mcp, threshold=0.5):
        """Check if finger is pointing sideways (more horizontal than vertical)"""
        dx = abs(lm[tip].x - lm[mcp].x)
        dy = abs(lm[tip].y - lm[mcp].y)
        return dx > dy * threshold

    def _fingers_together(self, lm, tip1, tip2, max_dist):
        """Check if two finger tips are close together"""
        return self._dist(lm, tip1, tip2) < max_dist

    def _get_finger_tips(self, lm):
        """Get positions of all finger tips"""
        return [lm[4], lm[8], lm[12], lm[16], lm[20]]

    def _count_extended_fingers(self, lm):
        """Count number of extended fingers (more reliable)"""
        count = 0
        threshold = 0.01  # Small threshold for extended check
        
        # Check each finger
        if self._is_extended(lm, self.INDEX_TIP, self.INDEX_PIP, threshold):
            count += 1
        if self._is_extended(lm, self.MIDDLE_TIP, self.MIDDLE_PIP, threshold):
            count += 1
        if self._is_extended(lm, self.RING_TIP, self.RING_PIP, threshold):
            count += 1
        if self._is_extended(lm, self.PINKY_TIP, self.PINKY_PIP, threshold):
            count += 1
        
        return count

    def recognize(self, lm, handedness="Right"):
        """
        Recognize an ASL letter from hand landmarks with improved angle handling.

        Args:
            lm: List of 21 MediaPipe hand landmarks
            handedness: "Left" or "Right"

        Returns:
            str: Recognized letter or "?"
        """
        # Basic finger extension checks
        thumb = self._thumb_extended(lm, handedness)
        index = self._is_extended(lm, self.INDEX_TIP, self.INDEX_PIP)
        middle = self._is_extended(lm, self.MIDDLE_TIP, self.MIDDLE_PIP)
        ring = self._is_extended(lm, self.RING_TIP, self.RING_PIP)
        pinky = self._is_extended(lm, self.PINKY_TIP, self.PINKY_PIP)

        n_up = sum([index, middle, ring, pinky])
        hs = self._hand_size(lm)
        if hs == 0:
            return "?"

        # Normalized distances between key points (using 3D for angle invariance)
        thumb_index = self._dist_3d(lm, 4, 8) / hs
        index_middle = self._dist_3d(lm, 8, 12) / hs
        middle_ring = self._dist_3d(lm, 12, 16) / hs
        
        # Additional distance metrics for better recognition
        thumb_middle = self._dist_3d(lm, 4, 12) / hs
        index_pinky = self._dist_3d(lm, 8, 20) / hs

        # Is index/middle pointing sideways?
        idx_sideways = self._is_pointing_sideways(lm, self.INDEX_TIP, self.INDEX_MCP, threshold=0.4)
        mid_sideways = self._is_pointing_sideways(lm, self.MIDDLE_TIP, self.MIDDLE_MCP, threshold=0.4)

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

        # --- G: index pointing sideways, others down, thumb not too close ---
        if idx_sideways and not middle and not ring and not pinky:
            if index or (lm[self.INDEX_TIP].y < lm[self.INDEX_MCP].y):
                if thumb_index > 0.2:  # Thumb not too close
                    return "G"

        # --- H: index + middle pointing sideways, others down ---
        if idx_sideways and mid_sideways and not ring and not pinky:
            if index_middle > 0.15:  # Fingers sufficiently spread
                return "H"

        # --- D: index up, thumb touching middle finger ---
        if index and not middle and not ring and not pinky:
            if thumb_middle < 0.5:  # Relaxed threshold for better angle tolerance
                return "D"

        # --- X: index hooked (tip between PIP and MCP), others down ---
        if not middle and not ring and not pinky and not thumb:
            if lm[self.INDEX_TIP].y > lm[self.INDEX_PIP].y and lm[self.INDEX_TIP].y < lm[self.INDEX_MCP].y:
                return "X"

        # --- V: index + middle up and spread, others down ---
        if index and middle and not ring and not pinky:
            if index_middle > 0.2:  # Spread threshold
                if not thumb:
                    return "V"
                else:
                    return "K"

        # --- R: index + middle up and slightly crossed/parallel ---
        if index and middle and not ring and not pinky and not thumb:
            # More forgiving R detection
            if index_middle < 0.4:  # Closer together than V
                return "R"

        # --- U: index + middle up and close together ---
        if index and middle and not ring and not pinky and not thumb:
            if index_middle < 0.25:
                return "U"

        # --- W: index + middle + ring up, pinky down ---
        if index and middle and ring and not pinky:
            return "W"

        # --- F: thumb-index pinch + middle/ring/pinky up ---
        if middle and ring and pinky and thumb_index < 0.2:  # Slightly relaxed
            return "F"

        # --- B: all 4 fingers up, thumb folded ---
        if index and middle and ring and pinky:
            return "B"

        # --- O: all fingers curved toward thumb (tips close to thumb) ---
        if n_up == 0 and not thumb:
            if thumb_index < 0.2:  # Relaxed threshold
                return "O"

        # --- C: curved hand, partially open, thumb to the side ---
        if n_up == 0 and thumb:
            if 0.2 < thumb_index < 0.5:  # Thumb visible but not pinched
                return "C"

        # --- E: all fingers curled, thumb across ---
        if n_up == 0 and not thumb:
            if thumb_index > 0.15:
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
