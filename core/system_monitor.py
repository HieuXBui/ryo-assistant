import psutil
import platform
import time
import threading
from datetime import datetime

class SystemMonitor:
    """Real-time system monitoring with sci-fi styling"""
    
    def __init__(self):
        self.cpu_percent = 0
        self.memory_percent = 0
        self.memory_used_gb = 0
        self.memory_total_gb = 0
        self.battery_percent = 0
        self.battery_plugged = False
        self.disk_usage = 0
        self.disk_used_gb = 0
        self.disk_total_gb = 0
        self.network_speed = 0
        self.temperature = 0
        self.uptime = 0
        self._running = False
        self._update_thread = None
        
    def start_monitoring(self):
        """Start real-time system monitoring"""
        self._running = True
        self._update_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._update_thread.start()
        
    def stop_monitoring(self):
        """Stop system monitoring"""
        self._running = False
        if self._update_thread:
            self._update_thread.join(timeout=1)
            
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self._running:
            try:
                self._update_system_info()
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                print(f"[ERROR] System monitoring error: {e}")
                time.sleep(5)
                
    def _update_system_info(self):
        """Update all system metrics"""
        # CPU Usage
        self.cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory Usage
        memory = psutil.virtual_memory()
        self.memory_percent = memory.percent
        self.memory_used_gb = memory.used / (1024**3)
        self.memory_total_gb = memory.total / (1024**3)
        
        # Battery Info
        try:
            battery = psutil.sensors_battery()
            if battery:
                self.battery_percent = battery.percent
                self.battery_plugged = battery.power_plugged
            else:
                self.battery_percent = 100
                self.battery_plugged = True
        except:
            self.battery_percent = 100
            self.battery_plugged = True
            
        # Disk Usage
        try:
            disk = psutil.disk_usage('/')
            self.disk_usage = disk.percent
            self.disk_used_gb = disk.used / (1024**3)
            self.disk_total_gb = disk.total / (1024**3)
        except:
            self.disk_usage = 0
            self.disk_used_gb = 0
            self.disk_total_gb = 0
            
        # Network Info
        try:
            net_io = psutil.net_io_counters()
            self.network_speed = (net_io.bytes_sent + net_io.bytes_recv) / (1024**2)  # MB
        except:
            self.network_speed = 0
            
        # System Uptime
        self.uptime = time.time() - psutil.boot_time()
        
        # Temperature (if available)
        try:
            temps = psutil.sensors_temperatures()
            if temps and 'coretemp' in temps:
                self.temperature = temps['coretemp'][0].current
            else:
                self.temperature = 45  # Default
        except:
            self.temperature = 45
            
    def get_system_info_text(self):
        """Get formatted system info for display with sci-fi styling"""
        # Format uptime
        uptime_seconds = int(self.uptime)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        
        # Format memory
        memory_text = f"{self.memory_used_gb:.1f}GB/{self.memory_total_gb:.1f}GB"
        
        # Format disk
        disk_text = f"{self.disk_used_gb:.1f}GB/{self.disk_total_gb:.1f}GB"
        
        # Battery status with sci-fi terms
        battery_status = "PLUGGED" if self.battery_plugged else "BATTERY"
        
        # OS info
        os_name = platform.system()
        os_version = platform.release()
        
        # Sci-fi styled text
        return {
            'cpu': f"PROCESSOR: {self.cpu_percent:.1f}%",
            'memory': f"MEMORY: {memory_text}",
            'battery': f"POWER: {self.battery_percent:.0f}% ({battery_status})",
            'disk': f"STORAGE: {disk_text}",
            'temp': f"THERMAL: {self.temperature:.1f}°C",
            'uptime': f"ONLINE: {hours:02d}:{minutes:02d}",
            'os': f"OS: {os_name} {os_version}",
            'network': f"NET: {self.network_speed:.1f}MB"
        }
        
    def get_progress_values(self):
        """Get progress bar values (0-100)"""
        return {
            'cpu': self.cpu_percent,
            'memory': self.memory_percent,
            'battery': self.battery_percent,
            'disk': self.disk_usage,
            'temp': min(self.temperature / 100, 1.0) * 100  # Normalize temperature
        }
        
    def get_status_color(self, metric, value):
        """Get color based on metric value (green/yellow/red)"""
        if metric == 'cpu':
            if value < 50: return "#00ff00"  # Green
            elif value < 80: return "#ffff00"  # Yellow
            else: return "#ff0000"  # Red
        elif metric == 'memory':
            if value < 60: return "#00ff00"
            elif value < 85: return "#ffff00"
            else: return "#ff0000"
        elif metric == 'battery':
            if value > 20: return "#00ff00"
            elif value > 10: return "#ffff00"
            else: return "#ff0000"
        elif metric == 'disk':
            if value < 70: return "#00ff00"
            elif value < 90: return "#ffff00"
            else: return "#ff0000"
        else:
            return "#00ff00"  # Default green 