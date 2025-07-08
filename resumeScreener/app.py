import gradio as gr
import os

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

def process_resume_and_job(job_desc, resume_file, resume_text, chat_history, user_msg):
    msg = user_msg.strip() or "Initial Analysis"
    reply = f"🔍 Response to **{msg}**"
    chat_history.append((msg, reply))
    return chat_history

def clear_chat():
    return []

def create_rma_interface():
    with gr.Blocks(
        title="Resume Match & Advisory (RMA) Agent",
        theme=gr.themes.Default(),
        css="""
        .main-container { max-width: 1500px; margin: auto; }
        .top-section { height: 30vh; min-height: 200px; }
        .bottom-section { height: 65vh; min-height: 400px; }
        .input-columns { height: 100%; }
        .input-columns .gr-textbox textarea { height: 180px !important; }
        .chat-container { height: 100%; }
        .chat-container .gr-chatbot { height: 300px !important; }
        """
    ) as demo:
        
        with gr.Column(elem_classes=["main-container"]):
            gr.Markdown("## 🎯 Resume Match & Advisory (RMA) Agent")
            gr.Markdown("Paste or upload your resume and job description to get real-time AI guidance.")
            
            # ─── TOP SECTION (30% height) ────────────────────────────────
            with gr.Row(elem_classes=["top-section"]):
                with gr.Column(scale=1, elem_classes=["input-columns"]):
                    gr.Markdown("### 📋 Job Description")
                    job_desc = gr.Textbox(
                        placeholder="Paste the job description here…",
                        lines=8,
                        label=""
                    )
                
                with gr.Column(scale=1, elem_classes=["input-columns"]):
                    gr.Markdown("### 📄 Resume")
                    with gr.Row():
                        resume_text = gr.Textbox(
                            placeholder="Paste your resume here or click 📎 to upload file…",
                            lines=8,
                            label="",
                            scale=10
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
            fn=process_resume_and_job,
            inputs=[job_desc, resume_file, resume_text, chatbot, qa_text],
            outputs=[chatbot]
        )
        
        clear_btn.click(fn=clear_chat, outputs=[chatbot])
    
    return demo

if __name__ == "__main__":
    create_rma_interface().launch(server_name="0.0.0.0", server_port=7860, share=True)