#!/usr/bin/env python3
"""
Start Flask app on first available port
"""
import socket
from main import app

def find_free_port():
    """Find a free port to use"""
    for port in range(8000, 9000):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except:
                continue
    return None

if __name__ == "__main__":
    port = find_free_port()
    if port:
        print(f"\n🚀 Starting SEO-Agent on port {port}")
        print(f"📱 Access at: http://142.93.194.81:{port}")
        print(f"🔧 Workshop Pro: http://142.93.194.81:{port}/workshop-pro")
        print("\nPress Ctrl+C to stop\n")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("❌ No free ports found between 8000-9000")