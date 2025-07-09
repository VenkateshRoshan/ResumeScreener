import gradio as gr
import os

# from main import process_resume_and_job # for direct gradio app testing

import requests

def handle_file_upload(file):
    if file is not None:
        filename = os.path.basename(file.name)
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".txt":
            with open(file.name, "r", encoding="utf-8") as f:
                return f.read(), f"✅ Uploaded: {filename}"
        else:
            return "[📄 Resume file will be processed automatically]", f"✅ Uploaded: {filename}"
    return "", ""

def analyze_resume_job(job_desc, resume_file, resume_text, chat_history, user_msg):
    """UI wrapper for the main workflow"""
    # -> for direct gradio app testing
    # try: 
    #     # Call the real function from main.py
    #     result = process_resume_and_job(
    #         job_description=job_desc,
    #         resume_file=resume_file, 
    #         resume_text=resume_text,
    #         chat_history=chat_history,
    #         user_message=user_msg
    #     )
    #     return result
        
    # except Exception as e:
    #     error_msg = f"Error: {str(e)}"
    #     chat_history.append(["Error", error_msg])
    #     return chat_history

    # -> for API call
    try:
        data = {
            "job_description": job_desc,
            "resume_text": resume_text,
        }
        files = {}
        if resume_file:
            # print(f"Resume file path from Gradio: {resume_file.name}")  # This will show the actual path
            # Open the file from the actual Gradio path and send it
            with open(resume_file.name, "rb") as f:
                files["resume_file"] = (
                    os.path.basename(resume_file.name),  # filename
                    f,  # file content
                    "application/pdf" if resume_file.name.endswith(".pdf") else "text/plain"  # content type
                )
                
                response = requests.post("http://localhost:8000/analyze", data=data, files=files)
                response.raise_for_status()
                result = response.json()

        else:
            response = requests.post("http://localhost:8000/analyze", data=data)
            response.raise_for_status()
            result = response.json()

        final_report = result["data"]["final_report"]
        chat_history.append(["AI", final_report])

        return chat_history
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        chat_history.append(["Error", error_msg])
        return chat_history

def clear_chat():
    return []

def create_rma_interface():
    with gr.Blocks(
        title="Resume Match & Advisory (RMA) Agent",
        theme=gr.themes.Default(),
        css="""
        .main-container { 
        max-width: 1500px; 
        margin: auto; 
    }
    .top-section {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 20px !important;
        height: 30vh;
        min-height: 300px;
    }
    .input-columns {
        width: 100% !important;
        min-width: 400px !important;
        max-width: 700px !important;
    }
    .input-columns .gr-textbox {
        width: 100% !important;
    }
    .input-columns .gr-textbox textarea { 
        height: 180px !important;
        width: 100% !important;
        resize: none !important;
        overflow-y: auto !important;
    }
    .bottom-section { 
        height: 65vh; 
        min-height: 400px; 
        margin-top: 20px;
    }
    .chat-container { 
        height: 100%; 
    }
    .chat-container .gr-chatbot { 
        height: 300px !important; 
    }
        """
    ) as demo:
        
        with gr.Column(elem_classes=["main-container"]):
            gr.Markdown("## 🎯 Resume Match & Advisory (RMA) Agent")
            gr.Markdown("Paste or upload your resume and job description to get real-time AI guidance.")
            
            # ─── TOP SECTION (30% height) ────────────────────────────────
            with gr.Row(elem_classes=["top-section"]):
                with gr.Column(scale=1, elem_classes=["input-columns"], min_width=400):
                    gr.Markdown("### 📋 Job Description")
                    job_desc = gr.Textbox(
                        placeholder="Paste the job description here…",
                        lines=8,
                        label="",
                        max_lines=10
                    )
                
                with gr.Column(scale=1, elem_classes=["input-columns"], min_width=400):
                    gr.Markdown("### 📄 Resume")
                    with gr.Row():
                        resume_text = gr.Textbox(
                            placeholder="Paste your resume here or click 📎 to upload file…",
                            lines=8,
                            label="",
                            scale=10,
                            max_lines=20
                        )
                        attach_btn = gr.Button("📎", size="sm", scale=1)
                    
                        resume_file = gr.File(
                            file_types=[".pdf", ".docx", ".txt"],
                            visible=False,
                            scale=1
                        )
                        file_status = gr.Markdown()
            
            # ─── BOTTOM SECTION (70% height) ───────────────────────────
            with gr.Column(elem_classes=["bottom-section"]):
                gr.Markdown("### 💬 AI Chat & Analysis")
                
                with gr.Column(elem_classes=["chat-container"]):
                    chatbot = gr.Chatbot(
                        label="",
                        show_copy_button=True
                    )
                    
                    with gr.Row():
                        analyze_btn = gr.Button("🔍 Analyze Match", variant="primary")
                        clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
                    
                    with gr.Row():
                        qa_text = gr.Textbox(placeholder="Enter your message here...", lines=1, label="")
        
        # Event handlers
        attach_btn.click(
            fn=lambda: gr.File(visible=True),
            outputs=[resume_file]
        )
        
        resume_file.change(
            fn=handle_file_upload,
            inputs=[resume_file],
            outputs=[resume_text, file_status]
        )
        
        analyze_btn.click(
            fn=analyze_resume_job, # from here the button calls the main.py function
            inputs=[job_desc, resume_file, resume_text, chatbot, qa_text],
            outputs=[chatbot]
        )
        
        clear_btn.click(fn=clear_chat, outputs=[chatbot])
    
    return demo

if __name__ == "__main__":
    create_rma_interface().launch(server_name="0.0.0.0", server_port=7860, share=True)