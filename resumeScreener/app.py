import gradio as gr
import os

# from main import process_resume_and_job # for direct gradio app testing

import requests

from dotenv import load_dotenv
load_dotenv()

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

def analyze_resume_job(job_desc, resume_file, resume_text, chat_history):
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
                
                response = requests.post("http://localhost:8345/analyze", data=data, files=files)
                response.raise_for_status()
                result = response.json()

        else:
            response = requests.post("http://localhost:8345/analyze", data=data)
            response.raise_for_status()
            result = response.json()

        final_report = result["data"]["final_report"]
        chat_history.append(["AI", final_report])
        # chat_history.append({"role": "AI", "content": final_report})

        return chat_history
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        chat_history.append(["Error", error_msg])
        # chat_history.append({"role": "Error", "content": error_msg})
        return chat_history

def clear_chat():
    return []

def create_rma_interface():
    with gr.Blocks(
        title="Resume Match & Advisory (RMA) Agent",
        theme=gr.themes.Default(),
        css="""
            /* Global Styles */
            .gradio-container {
                font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
                background: #1a1a1a !important;
            }
            
            /* Main Container */
            .main-container { 
                max-width: 1400px; 
                margin: 0 auto; 
                padding: 20px;
                background: linear-gradient(135deg, #1a1a1a 0%, #2c2c2c 100%) !important;
                min-height: 100vh;
            }
            
            /* Header Styling */
            .main-container h2 {
                color: #ffffff;
                text-align: center;
                margin-bottom: 10px;
                font-weight: 700;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            
            .main-container > .gr-markdown:nth-child(2) {
                text-align: center;
                color: #b0b0b0;
                margin-bottom: 30px;
                font-size: 16px;
            }
            
            /* Top Section - Input Areas */
            .top-section {
                display: grid !important;
                grid-template-columns: 1fr 1fr !important;
                gap: 25px !important;
                margin-bottom: 30px;
                background: #2a2a2a;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                border: 1px solid #404040;
            }
            
            /* Input Column Styling */
            .input-columns {
                width: 100% !important;
            }
            
            .input-columns h3 {
                color: #ffffff;
                margin-bottom: 15px !important;
                font-weight: 600;
                font-size: 18px;
                border-bottom: 2px solid #3498db;
                padding-bottom: 8px;
            }
            
            /* Textbox Styling - More Specific Selectors */
            .input-columns .gr-textbox {
                width: 100% !important;
                margin-bottom: 0 !important;
                height: 220px !important;
            }
            
            .input-columns .gr-textbox textarea,
            .input-columns .gr-textbox .gr-text-input,
            .input-columns textbox textarea,
            .resume-upload-row .gr-textbox textarea { 
                height: 220px !important;
                max-height: 220px !important;
                min-height: 220px !important;
                width: 100% !important;
                resize: none !important;
                overflow-y: auto !important;
                border: 2px solid #555555 !important;
                border-radius: 8px !important;
                padding: 15px !important;
                font-size: 14px !important;
                line-height: 1.5 !important;
                background: #333333 !important;
                color: #ffffff !important;
                transition: all 0.3s ease !important;
                box-sizing: border-box !important;
            }
            
            /* Force height override for all states */
            .input-columns .gr-textbox textarea[style*="height"],
            .resume-upload-row .gr-textbox textarea[style*="height"] {
                height: 220px !important;
                max-height: 220px !important;
                min-height: 220px !important;
            }
            
            .input-columns .gr-textbox textarea:focus { 
                border-color: #3498db !important;
                background: #3a3a3a !important;
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2) !important;
                outline: none !important;
                height: 220px !important;
                max-height: 220px !important;
                min-height: 220px !important;
            }
            
            /* File Upload Section */
            .resume-upload-row {
                display: flex !important;
                gap: 10px !important;
                align-items: flex-start !important;
            }
            
            .attach-btn {
                background: #3498db !important;
                color: white !important;
                border: none !important;
                border-radius: 6px !important;
                padding: 8px 12px !important;
                font-size: 16px !important;
                cursor: pointer !important;
                transition: all 0.3s ease !important;
                height: 40px !important;
                min-width: 45px !important;
            }
            
            .attach-btn:hover {
                background: #2980b9 !important;
                transform: translateY(-1px) !important;
            }
            
            /* Bottom Section - Chat Area */
            .bottom-section { 
                background: #2a2a2a;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                border: 1px solid #404040;
                min-height: 500px;
            }
            
            .bottom-section h3 {
                color: #ffffff;
                margin-bottom: 20px !important;
                font-weight: 600;
                font-size: 18px;
                border-bottom: 2px solid #e74c3c;
                padding-bottom: 8px;
            }
            
            /* Chat Container */
            .chat-container { 
                height: 100%; 
                display: flex;
                flex-direction: column;
            }
            
            .chat-container .gr-chatbot { 
                height: 400px !important; 
                border: 2px solid #555555 !important;
                border-radius: 8px !important;
                background: #333333 !important;
                margin-bottom: 20px !important;
            }
            
            /* Button Styling */
            .action-buttons {
                display: flex !important;
                gap: 15px !important;
                margin-bottom: 15px !important;
                justify-content: center !important;
            }
            
            .gr-button {
                border-radius: 8px !important;
                padding: 12px 24px !important;
                font-weight: 600 !important;
                font-size: 14px !important;
                transition: all 0.3s ease !important;
                border: none !important;
                cursor: pointer !important;
            }
            
            .gr-button.gr-button-primary {
                background: linear-gradient(135deg, #3498db, #2980b9) !important;
                color: white !important;
                box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3) !important;
            }
            
            .gr-button.gr-button-primary:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4) !important;
            }
            
            .gr-button.gr-button-secondary {
                background: linear-gradient(135deg, #95a5a6, #7f8c8d) !important;
                color: white !important;
                box-shadow: 0 4px 15px rgba(149, 165, 166, 0.3) !important;
            }
            
            .gr-button.gr-button-secondary:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(149, 165, 166, 0.4) !important;
            }
            
            /* Message Input */
            .message-input .gr-textbox textarea {
                border: 2px solid #555555 !important;
                border-radius: 8px !important;
                padding: 12px 15px !important;
                font-size: 14px !important;
                background: #333333 !important;
                color: #ffffff !important;
                transition: all 0.3s ease !important;
            }
            
            .message-input .gr-textbox textarea:focus {
                border-color: #3498db !important;
                background: #3a3a3a !important;
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2) !important;
                outline: none !important;
            }
            
            /* File Status */
            .file-status {
                color: #27ae60 !important;
                font-weight: 500 !important;
                margin-top: 8px !important;
            }
            
            /* Responsive Design */
            @media (max-width: 1200px) {
                .main-container {
                    max-width: 95%;
                    padding: 15px;
                }
                
                .top-section {
                    gap: 20px !important;
                    padding: 20px;
                }
            }
            
            @media (max-width: 768px) {
                .top-section {
                    grid-template-columns: 1fr !important;
                    gap: 20px !important;
                }
                
                .input-columns .gr-textbox textarea {
                    height: 180px !important;
                }
                
                .chat-container .gr-chatbot {
                    height: 300px !important;
                }
                
                .action-buttons {
                    flex-direction: column !important;
                    align-items: center !important;
                }
                
                .gr-button {
                    width: 200px !important;
                }
            }
            
            /* Custom Scrollbar */
            .gr-textbox textarea::-webkit-scrollbar {
                width: 8px;
            }
            
            .gr-textbox textarea::-webkit-scrollbar-track {
                background: #444444;
                border-radius: 4px;
            }
            
            .gr-textbox textarea::-webkit-scrollbar-thumb {
                background: #666666;
                border-radius: 4px;
            }
            
            .gr-textbox textarea::-webkit-scrollbar-thumb:hover {
                background: #888888;
            }
            
            /* Force override with JavaScript execution */
        """
    ) as demo:
        
        # Add JavaScript to force textarea height
        demo.load(
            fn=None,
            inputs=None,
            outputs=None,
            js="""
            function() {
                setTimeout(function() {
                    const textareas = document.querySelectorAll('.input-columns textarea, .resume-upload-row textarea');
                    textareas.forEach(function(textarea) {
                        textarea.style.height = '220px';
                        textarea.style.maxHeight = '220px';
                        textarea.style.minHeight = '220px';
                        textarea.style.resize = 'none';
                        textarea.style.overflowY = 'auto';
                        
                        // Override any dynamic changes
                        const observer = new MutationObserver(function(mutations) {
                            mutations.forEach(function(mutation) {
                                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                                    if (textarea.style.height !== '220px') {
                                        textarea.style.height = '220px';
                                        textarea.style.maxHeight = '220px';
                                        textarea.style.minHeight = '220px';
                                    }
                                }
                            });
                        });
                        observer.observe(textarea, { attributes: true, attributeFilter: ['style'] });
                    });
                }, 500);
            }
            """
        )
        
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
                    with gr.Row(elem_classes=["resume-upload-row"]):
                        resume_text = gr.Textbox(
                            placeholder="Paste your resume here or click 📎 to upload file…",
                            lines=10,
                            label="",
                            scale=10,
                            max_lines=10,
                            autoscroll=False,
                            show_copy_button=True
                        )
                        attach_btn = gr.Button("📎", size="sm", scale=1, elem_classes=["attach-btn"])
                    
                        resume_file = gr.File(
                            file_types=[".pdf", ".docx", ".txt"],
                            visible=False,
                            scale=1
                        )
                        file_status = gr.Markdown(elem_classes=["file-status"])
            
            # ─── BOTTOM SECTION (70% height) ───────────────────────────
            with gr.Column(elem_classes=["bottom-section"]):
                gr.Markdown("### 💬 AI Chat & Analysis")
                
                with gr.Column(elem_classes=["chat-container"]):
                    chatbot = gr.Chatbot(
                        label="",
                        show_copy_button=True,
                        # type="messages"
                    )
                    
                    with gr.Row(elem_classes=["action-buttons"]):
                        analyze_btn = gr.Button("🔍 Analyze Match", variant="primary")
                        clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
                    
                    # with gr.Row(elem_classes=["message-input"]):
                    #     qa_text = gr.Textbox(placeholder="Enter your message here...", lines=1, label="")
        
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
            inputs=[job_desc, resume_file, resume_text, chatbot], # TODO: qa_text for the chatbot integration
            outputs=[chatbot]
        )
        
        clear_btn.click(fn=clear_chat, outputs=[chatbot])
    
    return demo

if __name__ == "__main__":
    create_rma_interface().launch(server_name="0.0.0.0", server_port=7899, share=True)