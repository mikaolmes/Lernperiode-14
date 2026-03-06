# Finger Counter Documentation

## What is this?

This module counts how many fingers you're holding up (1-5) using MediaPipe hand detection.

## Files

- **`finger_counter.py`** - The counting logic (easy to modify)
- **`SignLanguage.py`** - Main camera app with finger counting integrated

## How to use as a teammate

### Option 1: Use the existing app
Just run `SignLanguage.py`:
```bash
python SignLanguage.py
```
Hold up your fingers (1-5) and the count will appear on screen!

### Option 2: Use the finger counter in your own code

```python
from finger_counter import FingerCounter

# Create counter instance
counter = FingerCounter()

# After getting detection_result from MediaPipe:
total_fingers, counts_per_hand = counter.count_all_hands(detection_result)

print(f"Total fingers: {total_fingers}")
print(f"Each hand: {counts_per_hand}")
```

## How it works

### Finger Detection Logic

Each hand has 21 landmarks (points). We check 5 fingers:

1. **Thumb** - Extended if tip is farther left/right than joint (depends on hand)
2. **Index, Middle, Ring, Pinky** - Extended if tip is ABOVE the middle joint

### Key Landmark Indices
- Thumb tip: 4
- Index tip: 8
- Middle tip: 12
- Ring tip: 16
- Pinky tip: 20

See `finger_counter.py` for the full code with comments!

## Modifying the code

### To change sensitivity:
Edit the comparison in `finger_counter.py`:
```python
# Make fingers harder to detect as "up":
if hand_landmarks[self.INDEX_TIP].y < hand_landmarks[self.INDEX_PIP].y - 0.02:
```

### To add your own gestures:
1. Copy `FingerCounter` class
2. Add your own logic using the 21 landmarks
3. Import and use in `SignLanguage.py`

## Requirements

```bash
pip install customtkinter opencv-python pillow mediapipe
```

You also need the model file: `hand_landmarker.task` (already in the repo)

## Troubleshooting

**Problem**: Finger count is wrong
- Make sure your hand is clearly visible
- Try better lighting
- Check if left/right hand detection is correct

**Problem**: Import error
- Make sure `finger_counter.py` is in the same folder as your script
- Or add to Python path: `import sys; sys.path.append('/path/to/folder')`

## Questions?

Ask Mateo or check the MediaPipe docs:
https://developers.google.com/mediapipe/solutions/vision/hand_landmarker
