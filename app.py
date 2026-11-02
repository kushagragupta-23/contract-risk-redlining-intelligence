import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gradio_app import demo

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    exports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
    os.makedirs(exports_dir, exist_ok=True)
    demo.launch(server_name="0.0.0.0", server_port=port, allowed_paths=[exports_dir])
