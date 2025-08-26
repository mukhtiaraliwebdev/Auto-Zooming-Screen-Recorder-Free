# Advanced Screen Recorder

**File Name:** `zoom_recorder.py`

## Overview
The Advanced Screen Recorder is a powerful, user-friendly desktop application designed for high-quality screen capture with intelligent zoom functionality. Built with Python and modern GUI frameworks, it combines professional recording capabilities with an intuitive interface, making it perfect for tutorials, presentations, software demonstrations, and content creation.

---

## 🌟 Key Features

### Smart Zoom Technology
- **Dynamic Cursor-Following Zoom**: Automatically centers zoom on cursor movement with smooth transitions  
- **Real-time Zoom Toggle**: Press `Ctrl` during recording to instantly zoom in/out up to 5× magnification  
- **Smooth Interpolation**: Eliminates jarring zoom transitions with customizable zoom speed  

### Professional Recording Controls
- **Hotkeys**
  - `Ctrl + S`: Start/Resume recording  
  - `P`: Pause/Resume recording  
  - `Q`: Stop recording  
- **Flexible Recording States**: Start, pause, resume, and stop with visual feedback  
- **Live Preview**: See exactly what's being recorded in real-time  

### Advanced Cursor Integration
- **Custom Cursor Overlay**: Supports transparent PNG cursor files for branded recordings  
- **Automatic Fallback**: Creates professional default cursor when custom file unavailable  
- **Scale Control**: Adjustable cursor size (25% to 100% scaling)  
- **Smooth Positioning**: Anti-aliased cursor rendering with proper alpha blending  

### User-Friendly Interface
- Modern Dark UI with intuitive controls  
- Live status indicators (color-coded)  
- Interactive preview window (480×270)  
- Drag-and-drop simplicity for file naming  

### High-Quality Output
- Multiple format support: MP4, AVI, custom  
- Adjustable frame rates: 10–60 FPS  
- Full HD recording at native resolution  
- Lossless, professional-grade compression  

---

## 🎯 Perfect For

### Content Creators
- Tutorial videos  
- Gaming content  
- Educational material  

### Business Professionals
- Software demos  
- Training materials  
- Client presentations  

### Developers & Designers
- Code reviews  
- UI/UX showcases  
- Bug reporting  

---

## 🔧 Technical Specifications

### System Requirements
- **OS**: Windows 7/8/10/11  
- **Python**: 3.7+ with pip  
- **RAM**: 2 GB min (4 GB recommended)  
- **Storage**: 100 MB app size, recordings vary  

### Dependencies
```bash
pip install opencv-python numpy mss pyautogui keyboard pillow
