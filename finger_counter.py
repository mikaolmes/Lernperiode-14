"""
Finger Counter Module
=====================
This module counts how many fingers are being held up (1-5).
Designed to be easy to use and modify by teammates.

How it works:
- Uses MediaPipe hand landmarks (21 points per hand)
- Checks if each finger is extended or folded
- Returns the count of extended fingers

Compatible with any MediaPipe hand detection result.
"""


class FingerCounter:
    """
    Counts extended fingers on a detected hand.
    
    Usage:
        counter = FingerCounter()
        num_fingers = counter.count_fingers(hand_landmarks, handedness)
    """
    
    # Landmark indices for fingertips and reference points
    # See MediaPipe hand landmark diagram for reference
    THUMB_TIP = 4
    THUMB_IP = 3
    
    INDEX_TIP = 8
    INDEX_PIP = 6
    
    MIDDLE_TIP = 12
    MIDDLE_PIP = 10
    
    RING_TIP = 16
    RING_PIP = 14
    
    PINKY_TIP = 20
    PINKY_PIP = 18
    
    WRIST = 0
    
    def __init__(self):
        """Initialize the finger counter."""
        pass
    
    def count_fingers(self, hand_landmarks, handedness="Right"):
        """
        Count how many fingers are extended.
        
        Args:
            hand_landmarks: List of MediaPipe landmarks (21 points)
            handedness: "Left" or "Right" hand (affects thumb logic)
            
        Returns:
            int: Number of extended fingers (0-5)
        """
        if not hand_landmarks:
            return 0
        
        fingers_up = 0
        
        # ================================
        # 1. Check THUMB (horizontal logic)
        # ================================
        # Thumb is extended if tip is farther from wrist than IP joint
        # Direction depends on left/right hand
        thumb_tip = hand_landmarks[self.THUMB_TIP]
        thumb_ip = hand_landmarks[self.THUMB_IP]
        
        if handedness == "Right":
            # Right hand: thumb extended if tip is to the RIGHT of IP joint
            if thumb_tip.x > thumb_ip.x:
                fingers_up += 1
        else:
            # Left hand: thumb extended if tip is to the LEFT of IP joint
            if thumb_tip.x < thumb_ip.x:
                fingers_up += 1
        
        # ================================
        # 2. Check OTHER FINGERS (vertical logic)
        # ================================
        # Finger is extended if tip is HIGHER (lower y value) than PIP joint
        
        # Index finger
        if hand_landmarks[self.INDEX_TIP].y < hand_landmarks[self.INDEX_PIP].y:
            fingers_up += 1
        
        # Middle finger
        if hand_landmarks[self.MIDDLE_TIP].y < hand_landmarks[self.MIDDLE_PIP].y:
            fingers_up += 1
        
        # Ring finger
        if hand_landmarks[self.RING_TIP].y < hand_landmarks[self.RING_PIP].y:
            fingers_up += 1
        
        # Pinky finger
        if hand_landmarks[self.PINKY_TIP].y < hand_landmarks[self.PINKY_PIP].y:
            fingers_up += 1
        
        return fingers_up
    
    def count_all_hands(self, detection_result):
        """
        Count fingers on ALL detected hands and return total.
        
        Args:
            detection_result: MediaPipe HandLandmarkerResult object
            
        Returns:
            int: Total fingers across all hands
            list: Finger count for each individual hand
        """
        if not detection_result.hand_landmarks:
            return 0, []
        
        total_fingers = 0
        individual_counts = []
        
        # Process each detected hand
        for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
            # Get handedness (left/right)
            handedness = "Right"
            if detection_result.handedness:
                hand_category = detection_result.handedness[idx][0]
                handedness = hand_category.category_name
            
            # Count fingers on this hand
            count = self.count_fingers(hand_landmarks, handedness)
            total_fingers += count
            individual_counts.append(count)
        
        return total_fingers, individual_counts


# ================================
# Simple Test Function
# ================================
def test_finger_counter():
    """
    Simple test to verify the module works.
    Print instructions for teammates.
    """
    print("=" * 50)
    print("Finger Counter Module - Ready!")
    print("=" * 50)
    print("\nHow to use in your code:\n")
    print("from finger_counter import FingerCounter")
    print("counter = FingerCounter()")
    print("num_fingers = counter.count_fingers(hand_landmarks, handedness)")
    print("\nOR for all hands:")
    print("total, counts = counter.count_all_hands(detection_result)")
    print("=" * 50)


if __name__ == "__main__":
    test_finger_counter()
