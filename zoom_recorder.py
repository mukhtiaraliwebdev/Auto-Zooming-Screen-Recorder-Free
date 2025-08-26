import cv2
import numpy as np
import mss
import pyautogui
import keyboard
import time
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class ScreenRecorderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Screen Recorder")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Recording state
        self.recording = False
        self.paused = False
        self.out = None
        self.recording_thread = None
        
        # Settings
        self.output_file = ""
        self.fps = 20.0
        self.zoom_factor = 2.0
        self.zoom_speed = 0.1
        self.follow_speed = 0.08
        self.cursor_scale = 0.4
        
        # Screen settings
        self.screen_width, self.screen_height = pyautogui.size()
        self.aspect_ratio = self.screen_width / self.screen_height
        
        # Monitor setup
        self.monitor = {"top": 0, "left": 0, "width": self.screen_width, "height": self.screen_height}
        
        # Load cursor
        self.load_cursor()
        
        # Zoom and cursor states
        self.target_zoom = 1.0
        self.current_zoom = 1.0
        self.cursor_x = self.screen_width // 2
        self.cursor_y = self.screen_height // 2
        
        # Setup GUI
        self.setup_gui()
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()
        
        # Start preview
        self.start_preview()
        
    def load_cursor(self):
        """Load and resize cursor image"""
        try:
            self.cursor_img = cv2.imread("cursor.png", cv2.IMREAD_UNCHANGED)
            if self.cursor_img is None:
                # Create a simple cursor if file not found
                self.cursor_img = self.create_default_cursor()
            
            # Resize cursor
            cursor_h, cursor_w = self.cursor_img.shape[:2]
            new_w = int(cursor_w * self.cursor_scale)
            new_h = int(cursor_h * self.cursor_scale)
            self.cursor_img = cv2.resize(self.cursor_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        except Exception as e:
            self.cursor_img = self.create_default_cursor()
    
    def create_default_cursor(self):
        """Create a simple default cursor"""
        cursor = np.zeros((20, 15, 4), dtype=np.uint8)
        # White cursor with black outline
        cursor[2:18, 2:13, :3] = [255, 255, 255]  # White interior
        cursor[1:19, 1:14, :3] = [0, 0, 0]  # Black outline
        cursor[2:18, 2:13, :3] = [255, 255, 255]  # White interior (overwrite)
        cursor[:, :, 3] = 255  # Full alpha
        # Make arrow shape
        for i in range(15):
            for j in range(min(i, 10)):
                if j < 15 and i < 20:
                    cursor[i, j, :3] = [255, 255, 255]
                    cursor[i, j, 3] = 255
        return cursor
    
    def setup_gui(self):
        """Setup the GUI interface"""
        # Title
        title_label = tk.Label(self.root, text="Advanced Screen Recorder", 
                              font=("Arial", 24, "bold"), fg='white', bg='#2b2b2b')
        title_label.pack(pady=20)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Left panel - Controls
        control_frame = tk.Frame(main_frame, bg='#3b3b3b', relief='raised', bd=2)
        control_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Controls title
        controls_title = tk.Label(control_frame, text="Recording Controls", 
                                 font=("Arial", 16, "bold"), fg='white', bg='#3b3b3b')
        controls_title.pack(pady=15)
        
        # File selection
        file_frame = tk.Frame(control_frame, bg='#3b3b3b')
        file_frame.pack(pady=10, padx=15, fill='x')
        
        tk.Label(file_frame, text="Output File:", font=("Arial", 10, "bold"), 
                fg='white', bg='#3b3b3b').pack(anchor='w')
        
        self.file_var = tk.StringVar(value="screen_record.mp4")
        self.file_entry = tk.Entry(file_frame, textvariable=self.file_var, 
                                  font=("Arial", 10), width=25)
        self.file_entry.pack(pady=5, fill='x')
        
        browse_btn = tk.Button(file_frame, text="Browse", command=self.browse_file,
                              bg='#4a4a4a', fg='white', font=("Arial", 9), 
                              relief='flat', padx=10)
        browse_btn.pack(pady=5)
        
        # Recording buttons
        button_frame = tk.Frame(control_frame, bg='#3b3b3b')
        button_frame.pack(pady=20, padx=15, fill='x')
        
        self.start_btn = tk.Button(button_frame, text="▶ Start Recording\n(Ctrl+S)", 
                                  command=self.start_recording, bg='#28a745', fg='white',
                                  font=("Arial", 10, "bold"), relief='flat', 
                                  padx=20, pady=10)
        self.start_btn.pack(pady=5, fill='x')
        
        self.pause_btn = tk.Button(button_frame, text="⏸ Pause Recording\n(P)", 
                                  command=self.pause_recording, bg='#ffc107', fg='black',
                                  font=("Arial", 10, "bold"), relief='flat', 
                                  padx=20, pady=10, state='disabled')
        self.pause_btn.pack(pady=5, fill='x')
        
        self.stop_btn = tk.Button(button_frame, text="⏹ Stop Recording\n(Q)", 
                                 command=self.stop_recording, bg='#dc3545', fg='white',
                                 font=("Arial", 10, "bold"), relief='flat', 
                                 padx=20, pady=10, state='disabled')
        self.stop_btn.pack(pady=5, fill='x')
        
        # Status
        status_frame = tk.Frame(control_frame, bg='#3b3b3b')
        status_frame.pack(pady=15, padx=15, fill='x')
        
        tk.Label(status_frame, text="Status:", font=("Arial", 10, "bold"), 
                fg='white', bg='#3b3b3b').pack(anchor='w')
        
        self.status_var = tk.StringVar(value="Ready to record")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, 
                                    font=("Arial", 10), fg='#90EE90', bg='#3b3b3b')
        self.status_label.pack(anchor='w', pady=5)
        
        # Settings
        settings_frame = tk.LabelFrame(control_frame, text="Settings", 
                                      font=("Arial", 10, "bold"), fg='white', 
                                      bg='#3b3b3b', bd=2, relief='groove')
        settings_frame.pack(pady=15, padx=15, fill='x')
        
        # FPS setting
        tk.Label(settings_frame, text="FPS:", fg='white', bg='#3b3b3b').pack(anchor='w')
        self.fps_var = tk.DoubleVar(value=self.fps)
        fps_spinbox = tk.Spinbox(settings_frame, from_=10, to=60, increment=5, 
                                textvariable=self.fps_var, width=10)
        fps_spinbox.pack(anchor='w', pady=2)
        
        # Zoom factor
        tk.Label(settings_frame, text="Zoom Factor:", fg='white', bg='#3b3b3b').pack(anchor='w', pady=(10,0))
        self.zoom_var = tk.DoubleVar(value=self.zoom_factor)
        zoom_spinbox = tk.Spinbox(settings_frame, from_=1.5, to=5.0, increment=0.5, 
                                 textvariable=self.zoom_var, width=10)
        zoom_spinbox.pack(anchor='w', pady=2)
        
        # Instructions
        instructions_frame = tk.Frame(control_frame, bg='#3b3b3b')
        instructions_frame.pack(pady=20, padx=15, fill='x')
        
        tk.Label(instructions_frame, text="Instructions:", font=("Arial", 10, "bold"), 
                fg='white', bg='#3b3b3b').pack(anchor='w')
        
        instructions = """• Ctrl+S: Start/Resume recording
• Q: Stop recording  
• P: Pause recording
• Ctrl: Toggle zoom while recording
• Close window to exit"""
        
        tk.Label(instructions_frame, text=instructions, font=("Arial", 9), 
                fg='#cccccc', bg='#3b3b3b', justify='left').pack(anchor='w', pady=5)
        
        # Right panel - Preview
        preview_frame = tk.Frame(main_frame, bg='#3b3b3b', relief='raised', bd=2)
        preview_frame.pack(side='right', expand=True, fill='both')
        
        preview_title = tk.Label(preview_frame, text="Live Preview", 
                                font=("Arial", 16, "bold"), fg='white', bg='#3b3b3b')
        preview_title.pack(pady=15)
        
        # Preview canvas
        self.preview_canvas = tk.Canvas(preview_frame, bg='black', width=480, height=270)
        self.preview_canvas.pack(expand=True, padx=20, pady=20)
        
    def browse_file(self):
        """Open file dialog to select output file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("All files", "*.*")],
            title="Save recording as..."
        )
        if file_path:
            self.file_var.set(file_path)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-s>', lambda e: self.start_recording())
        self.root.bind('<Control-S>', lambda e: self.start_recording())
        self.root.bind('q', lambda e: self.stop_recording())
        self.root.bind('Q', lambda e: self.stop_recording())
        self.root.bind('p', lambda e: self.pause_recording())
        self.root.bind('P', lambda e: self.pause_recording())
        
        # Focus on root to capture key events
        self.root.focus_set()
    
    def overlay_cursor(self, frame, cursor, pos_x, pos_y):
        """Overlay cursor image with alpha channel on frame"""
        try:
            if len(cursor.shape) < 3 or cursor.shape[2] < 4:
                return frame
                
            h, w = cursor.shape[:2]
            
            # Clamp position to frame bounds
            pos_x = max(0, min(pos_x, frame.shape[1] - 1))
            pos_y = max(0, min(pos_y, frame.shape[0] - 1))
            
            # Calculate actual overlay dimensions
            end_y = min(pos_y + h, frame.shape[0])
            end_x = min(pos_x + w, frame.shape[1])
            actual_h = end_y - pos_y
            actual_w = end_x - pos_x
            
            if actual_h <= 0 or actual_w <= 0:
                return frame
            
            # Get the parts we need
            cursor_part = cursor[:actual_h, :actual_w]
            cursor_rgb = cursor_part[:, :, :3].astype(np.float32)
            alpha = cursor_part[:, :, 3].astype(np.float32) / 255.0
            
            # Get ROI from frame
            roi = frame[pos_y:end_y, pos_x:end_x].astype(np.float32)
            
            # Ensure dimensions match
            if roi.shape[:2] != alpha.shape[:2]:
                return frame
            
            # Expand alpha to 3 channels for broadcasting
            alpha_3d = np.stack([alpha, alpha, alpha], axis=2)
            
            # Blend
            blended = (1 - alpha_3d) * roi + alpha_3d * cursor_rgb
            
            # Put back into frame
            frame[pos_y:end_y, pos_x:end_x] = blended.astype(np.uint8)
            
        except Exception as e:
            # If cursor overlay fails, just return the frame without cursor
            pass
            
        return frame
    
    def capture_frame(self, sct=None):
        """Capture and process a single frame"""
        try:
            # Create MSS instance if not provided (for threading)
            if sct is None:
                sct = mss.mss()
            
            # Update settings from GUI
            self.fps = self.fps_var.get()
            self.zoom_factor = self.zoom_var.get()
            
            # Capture screen
            sct_img = sct.grab(self.monitor)
            frame = np.array(sct_img)[:, :, :3].copy()
            
            # Check for zoom toggle (only during recording)
            if self.recording and keyboard.is_pressed('ctrl'):
                self.target_zoom = self.zoom_factor if self.target_zoom == 1.0 else 1.0
                time.sleep(0.1)  # debounce
            
            # Smooth zoom transition
            if abs(self.current_zoom - self.target_zoom) > 0.001:
                self.current_zoom += (self.target_zoom - self.current_zoom) * self.zoom_speed
            
            # Smooth cursor follow
            try:
                mouse_x, mouse_y = pyautogui.position()
                self.cursor_x += (mouse_x - self.cursor_x) * self.follow_speed
                self.cursor_y += (mouse_y - self.cursor_y) * self.follow_speed
            except:
                mouse_x, mouse_y = self.cursor_x, self.cursor_y
            
            if self.current_zoom > 1.01:
                # Crop for zoom
                crop_w = int(self.screen_width / self.current_zoom)
                crop_h = int(crop_w / self.aspect_ratio)
                
                left = max(0, min(self.screen_width - crop_w, int(self.cursor_x - crop_w // 2)))
                top = max(0, min(self.screen_height - crop_h, int(self.cursor_y - crop_h // 2)))
                right = left + crop_w
                bottom = top + crop_h
                
                zoom_frame = frame[top:bottom, left:right]
                frame = cv2.resize(zoom_frame, (self.screen_width, self.screen_height), 
                                 interpolation=cv2.INTER_LINEAR)
                
                # Adjust mouse position for zoom
                mouse_draw_x = int((mouse_x - left) * (self.screen_width / crop_w))
                mouse_draw_y = int((mouse_y - top) * (self.screen_height / crop_h))
            else:
                mouse_draw_x, mouse_draw_y = mouse_x, mouse_y
            
            # Overlay cursor
            frame = self.overlay_cursor(frame, self.cursor_img, mouse_draw_x, mouse_draw_y)
            
            return frame
            
        except Exception as e:
            # Return a black frame if capture fails
            return np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
    
    def update_preview(self):
        """Update preview canvas"""
        try:
            frame = self.capture_frame()
            
            # Resize for preview
            preview_frame = cv2.resize(frame, (480, 270))
            preview_frame = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage
            from PIL import Image, ImageTk
            pil_image = Image.fromarray(preview_frame)
            photo = ImageTk.PhotoImage(image=pil_image)
            
            # Update canvas
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(240, 135, image=photo)
            self.preview_canvas.image = photo  # Keep reference
            
        except Exception as e:
            pass  # Continue even if preview fails
    
    def start_preview(self):
        """Start the preview loop"""
        self.update_preview()
        self.root.after(50, self.start_preview)  # Update every 50ms
    
    def recording_loop(self):
        """Main recording loop"""
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(self.output_file, fourcc, self.fps, 
                                  (self.screen_width, self.screen_height))
        
        while self.recording:
            if not self.paused:
                frame = self.capture_frame()
                self.out.write(frame)
            
            time.sleep(1.0 / self.fps)
        
        if self.out:
            self.out.release()
            self.out = None
    
    def start_recording(self):
        """Start recording"""
        if self.recording:
            if self.paused:
                self.paused = False
                self.status_var.set("Recording...")
                self.status_label.config(fg='#90EE90')
                self.pause_btn.config(text="⏸ Pause Recording\n(P)")
            return
        
        self.output_file = self.file_var.get()
        if not self.output_file:
            messagebox.showerror("Error", "Please specify an output file name.")
            return
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.output_file)), exist_ok=True)
        
        self.recording = True
        self.paused = False
        self.target_zoom = 1.0
        self.current_zoom = 1.0
        
        # Update UI
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.stop_btn.config(state='normal')
        self.status_var.set("Recording...")
        self.status_label.config(fg='#90EE90')
        
        # Start recording thread
        self.recording_thread = threading.Thread(target=self.recording_loop, daemon=True)
        self.recording_thread.start()
        
        messagebox.showinfo("Recording Started", "Recording started! Use Ctrl to toggle zoom while recording.")
    
    def pause_recording(self):
        """Pause/resume recording"""
        if not self.recording:
            return
        
        self.paused = not self.paused
        
        if self.paused:
            self.status_var.set("Paused")
            self.status_label.config(fg='#ffc107')
            self.pause_btn.config(text="▶ Resume Recording\n(P)")
        else:
            self.status_var.set("Recording...")
            self.status_label.config(fg='#90EE90')
            self.pause_btn.config(text="⏸ Pause Recording\n(P)")
    
    def stop_recording(self):
        """Stop recording"""
        if not self.recording:
            return
        
        self.recording = False
        self.paused = False
        
        # Wait for recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2.0)
        
        # Update UI
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled', text="⏸ Pause Recording\n(P)")
        self.stop_btn.config(state='disabled')
        self.status_var.set("Recording stopped")
        self.status_label.config(fg='#cccccc')
        
        messagebox.showinfo("Recording Stopped", f"Recording saved to:\n{self.output_file}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.recording:
            self.stop_recording()
        
        self.root.quit()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ScreenRecorderGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()