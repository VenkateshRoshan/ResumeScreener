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
        theme=gr.themes.Soft(
            primary_hue="orange",
            secondary_hue="neutral",
            neutral_hue="gray"
        ),
        css="""
            /* Global Styles */
            .gradio-container {
                font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
                background: linear-gradient(135deg, #1a1a1a 0%, #2c2c2c 100%) !important;
            }
            
            /* Main Container */
            .main-container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
                background: linear-gradient(135deg, #1a1a1a 0%, #2c2c2c 100%) !important;
                min-height: 100vh;
            }
            
            /* Header Styling */
            .header-section {
                text-align: center;
                margin-bottom: 30px;
                padding: 15px;
                background: linear-gradient(135deg, #27ae60, #2ecc71);
                border-radius: 15px;
                box-shadow: 0 6px 24px rgba(39, 174, 96, 0.3);
            }
            
            .header-section h1 {
                color: white;
                font-size: 2em;
                font-weight: 700;
                margin: 0;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            
            .header-section p {
                color: #e8f5e8;
                font-size: 14px;
                margin: 8px 0 0 0;
                font-weight: 500;
            }
            
            /* Input Sections */
            .input-section {
                background: #2a2a2a;
                border-radius: 16px;
                padding: 25px;
                margin-bottom: 25px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 2px solid #404040;
                transition: all 0.3s ease;
            }
            
            .input-section:hover {
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
                transform: translateY(-2px);
            }
            
            .section-title {
                color: #27ae60;
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 3px solid #2ecc71;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            /* Job Description Section */
            .job-desc-section .gr-textbox textarea {
                height: 200px !important;
                max-height: 200px !important;
                min-height: 200px !important;
                border: 2px solid #555555 !important;
                border-radius: 12px !important;
                padding: 15px !important;
                font-size: 14px !important;
                line-height: 1.6 !important;
                background: #333333 !important;
                color: #ffffff !important;
                transition: all 0.3s ease !important;
                resize: none !important;
                overflow-y: auto !important;
            }
            
            .job-desc-section .gr-textbox textarea:focus {
                border-color: #2ecc71 !important;
                background: #3a3a3a !important;
                box-shadow: 0 0 0 4px rgba(46, 204, 113, 0.2) !important;
                outline: none !important;
            }
            
            /* Resume Section */
            .resume-section {
                position: relative;
            }
            
            .resume-options {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-top: 15px;
            }
            
            .upload-option, .text-option {
                padding: 20px;
                border: 2px dashed #fde2d3;
                border-radius: 12px;
                text-align: center;
                transition: all 0.3s ease;
                background: #fefefe;
            }
            
            .upload-option:hover, .text-option:hover {
                border-color: #f39c12;
                background: #fff8f5;
                transform: translateY(-2px);
            }
            
            .upload-option.active, .text-option.active {
                border-color: #f39c12;
                background: #fff8f5;
                box-shadow: 0 4px 15px rgba(243, 156, 18, 0.2);
            }
            
            .option-icon {
                font-size: 2em;
                margin-bottom: 10px;
                color: #f39c12;
            }
            
            .option-title {
                font-weight: 600;
                color: #d35400;
                margin-bottom: 5px;
            }
            
            .option-desc {
                font-size: 12px;
                color: #7d4f36;
            }
            
            .resume-text-area .gr-textbox textarea {
                height: 200px !important;
                max-height: 200px !important;
                min-height: 200px !important;
                border: 2px solid #555555 !important;
                border-radius: 12px !important;
                padding: 15px !important;
                font-size: 14px !important;
                line-height: 1.6 !important;
                background: #333333 !important;
                color: #ffffff !important;
                transition: all 0.3s ease !important;
                resize: none !important;
                overflow-y: auto !important;
            }
            
            .resume-text-area .gr-textbox textarea:focus {
                border-color: #2ecc71 !important;
                background: #3a3a3a !important;
                box-shadow: 0 0 0 4px rgba(46, 204, 113, 0.2) !important;
                outline: none !important;
            }
            
            /* File Upload Styling */
            .gr-file {
                border: 2px dashed #555555 !important;
                border-radius: 12px !important;
                background: #333333 !important;
                padding: 20px !important;
                text-align: center !important;
            }
            
            .gr-file:hover {
                border-color: #2ecc71 !important;
                background: #3a3a3a !important;
            }
            
            /* Process Button */
            .process-section {
                text-align: center;
                margin: 30px 0;
            }
            
            .process-btn {
                background: linear-gradient(135deg, #27ae60, #2ecc71) !important;
                color: white !important;
                border: none !important;
                border-radius: 50px !important;
                padding: 15px 40px !important;
                font-size: 18px !important;
                font-weight: 600 !important;
                cursor: pointer !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 6px 20px rgba(39, 174, 96, 0.3) !important;
                text-transform: uppercase !important;
                letter-spacing: 1px !important;
            }
            
            .process-btn:hover {
                transform: translateY(-3px) !important;
                box-shadow: 0 8px 25px rgba(39, 174, 96, 0.4) !important;
                background: linear-gradient(135deg, #2ecc71, #27ae60) !important;
            }
            
            .process-btn:active {
                transform: translateY(-1px) !important;
            }
            
            /* Analyzing Button State */
            .process-btn[value*="Analyzing"] {
                background: linear-gradient(135deg, #95a5a6, #7f8c8d) !important;
                cursor: not-allowed !important;
                opacity: 0.8 !important;
            }
            
            .process-btn[value*="Analyzing"]:hover {
                transform: none !important;
                box-shadow: 0 6px 20px rgba(243, 156, 18, 0.3) !important;
            }
            
            /* Results Section */
            .results-section {
                background: #2a2a2a;
                border-radius: 16px;
                padding: 25px;
                margin-top: 25px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 2px solid #404040;
                border-left: 6px solid #2ecc71;
            }
            
            .results-section h3 {
                color: #27ae60;
                font-size: 22px;
                font-weight: 600;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .results-content {
                background: #333333;
                border: 1px solid #555555;
                border-radius: 12px;
                padding: 20px;
                min-height: 300px;
                font-size: 14px;
                line-height: 1.6;
                color: #ffffff;
                white-space: pre-wrap;
                overflow-y: auto;
                max-height: 500px;
            }
            
            .results-content:empty::before {
                content: "Click 'Process' to analyze your resume and job description match...";
                color: #999;
                font-style: italic;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 260px;
            }
            
            /* Loading State */
            .loading {
                text-align: center;
                padding: 40px;
                color: #f39c12;
            }
            
            .loading::before {
                content: "🔄 ";
                font-size: 1.5em;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            
            /* File Status */
            .file-status {
                margin-top: 10px;
                padding: 8px 12px;
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }
            
            /* Responsive Design */
            @media (max-width: 768px) {
                .main-container {
                    padding: 15px;
                }
                
                .resume-options {
                    grid-template-columns: 1fr;
                    gap: 15px;
                }
                
                .header-section h1 {
                    font-size: 2em;
                }
                
                .process-btn {
                    padding: 12px 30px !important;
                    font-size: 16px !important;
                }
            }
            
            /* Custom Scrollbar */
            .gr-textbox textarea::-webkit-scrollbar,
            .results-content::-webkit-scrollbar {
                width: 8px;
            }
            
            .gr-textbox textarea::-webkit-scrollbar-track,
            .results-content::-webkit-scrollbar-track {
                background: #404040;
                border-radius: 4px;
            }
            
            .gr-textbox textarea::-webkit-scrollbar-thumb,
            .results-content::-webkit-scrollbar-thumb {
                background: #27ae60;
                border-radius: 4px;
            }
            
            .gr-textbox textarea::-webkit-scrollbar-thumb:hover,
            .results-content::-webkit-scrollbar-thumb:hover {
                background: #2ecc71;
            }
            
            /* Hide elements initially */
            .hidden {
                display: none !important;
            }
            
            /* Toggle Buttons */
            .resume-section .gr-button {
                padding: 8px 16px !important;
                font-size: 13px !important;
                border-radius: 8px !important;
                margin: 0 5px !important;
                min-width: 120px !important;
                background: #404040 !important;
                color: #ffffff !important;
                border: 1px solid #555555 !important;
                transition: all 0.3s ease !important;
            }
            
            .resume-section .gr-button:hover {
                background: #27ae60 !important;
                color: white !important;
                border-color: #2ecc71 !important;
                transform: translateY(-1px) !important;
            }
            
            .resume-section .gr-button:active {
                background: #2ecc71 !important;
                transform: translateY(0) !important;
            }
        """
    ) as demo:
        
        with gr.Column(elem_classes=["main-container"]):
            # Header Section
            with gr.Column(elem_classes=["header-section"]):
                gr.HTML("<h1>🎯 Resume Match & Advisory Agent</h1>")
                gr.HTML("<p>Get AI-powered insights on how well your resume matches the job description</p>")
            
            # Job Description Section
            with gr.Column(elem_classes=["input-section", "job-desc-section"]):
                gr.HTML('<div class="section-title">📋 Job Description</div>')
                job_desc = gr.Textbox(
                    placeholder="Enter the complete job description here...\n\nInclude:\n• Job title and company\n• Required skills and qualifications\n• Job responsibilities\n• Experience requirements",
                    lines=8,
                    label="",
                    show_copy_button=True
                )
            
            # Resume Section
            with gr.Column(elem_classes=["input-section", "resume-section"]):
                gr.HTML('<div class="section-title">📄 Resume</div>')
                
                # Toggle buttons for resume input method
                with gr.Row():
                    upload_btn = gr.Button("📎 Upload File", size="sm", variant="secondary")
                    text_btn = gr.Button("✏️ Paste Text", size="sm", variant="secondary")
                
                # Resume input area (both options in same space)
                with gr.Column():
                    resume_file = gr.File(
                        file_types=[".pdf", ".docx", ".txt"],
                        label="Choose Resume File",
                        visible=False
                    )
                    resume_text = gr.Textbox(
                        placeholder="Paste your resume text here...\n\nInclude:\n• Contact information\n• Work experience\n• Education\n• Skills\n• Achievements",
                        lines=8,
                        label="Resume Text",
                        show_copy_button=True,
                        visible=False,
                        elem_classes=["resume-text-area"]
                    )
                    file_status = gr.HTML("")
            
            # Process Button
            with gr.Column(elem_classes=["process-section"]):
                process_btn = gr.Button("🚀 Process & Analyze", elem_classes=["process-btn"], variant="primary")
            
            # Results Section (Initially hidden)
            with gr.Column(elem_classes=["results-section"], visible=False) as results_section:
                gr.HTML('<h3>📊 Analysis Results</h3>')
                results_display = gr.HTML("", elem_classes=["results-content"])
        
        # Event handlers
        def handle_file_upload_new(file):
            if file is not None:
                filename = os.path.basename(file.name)
                ext = os.path.splitext(filename)[1].lower()
                if ext == ".txt":
                    with open(file.name, "r", encoding="utf-8") as f:
                        content = f.read()
                    return content, f'<div class="file-status">✅ Uploaded: {filename}</div>', ""
                else:
                    return "", f'<div class="file-status">✅ Uploaded: {filename}</div>', "[📄 Resume file will be processed automatically]"
            return "", "", ""
        
        def process_analysis(job_desc, resume_file, resume_text):
            if not job_desc.strip():
                return gr.update(visible=True), "<div style='color: #e74c3c; padding: 20px; text-align: center;'>❌ Please enter a job description</div>", gr.update(value="🚀 Process & Analyze")
            
            if not resume_file and not resume_text.strip():
                return gr.update(visible=True), "<div style='color: #e74c3c; padding: 20px; text-align: center;'>❌ Please upload a resume file or paste resume text</div>", gr.update(value="🚀 Process & Analyze")
            
            # Show loading state
            loading_html = "<div class='loading'>Analyzing your resume and job description...</div>"
            
            try:
                # API call logic (same as before)
                data = {
                    "job_description": job_desc,
                    "resume_text": resume_text,
                }
                files = {}
                if resume_file:
                    with open(resume_file.name, "rb") as f:
                        files["resume_file"] = (
                            os.path.basename(resume_file.name),
                            f,
                            "application/pdf" if resume_file.name.endswith(".pdf") else "text/plain"
                        )
                        response = requests.post("http://localhost:8345/analyze", data=data, files=files)
                        response.raise_for_status()
                        result = response.json()
                else:
                    response = requests.post("http://localhost:8345/analyze", data=data)
                    response.raise_for_status()
                    result = response.json()

                final_report = result["data"]["final_report"]
                
                # Format the results nicely
                formatted_result = f"""
<div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #f39c12;">
<h4 style="color: #d35400; margin-top: 0;">📋 Analysis Report</h4>
<div style="white-space: pre-wrap; line-height: 1.6; color: #5d4037;">
{final_report}
</div>
</div>
                """
                
                return gr.update(visible=True), formatted_result, gr.update(value="🚀 Process & Analyze")
                
            except Exception as e:
                error_html = f"""
<div style="background: #f8d7da; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545; color: #721c24;">
<h4 style="margin-top: 0;">❌ Error</h4>
<p>Failed to analyze resume: {str(e)}</p>
<p><small>Please check if the API server is running on localhost:8345</small></p>
</div>
                """
                return gr.update(visible=True), error_html, gr.update(value="🚀 Process & Analyze")
        
        # Event bindings
        upload_btn.click(
            fn=lambda: (gr.update(visible=True), gr.update(visible=False)),
            inputs=[],
            outputs=[resume_file, resume_text]
        )
        
        text_btn.click(
            fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
            inputs=[],
            outputs=[resume_file, resume_text]
        )
        
        resume_file.change(
            fn=handle_file_upload_new,
            inputs=[resume_file],
            outputs=[resume_text, file_status, resume_text]
        )
        
        process_btn.click(
            fn=lambda: gr.update(value="🔄 Analyzing..."),
            inputs=[],
            outputs=[process_btn]
        ).then(
            fn=process_analysis,
            inputs=[job_desc, resume_file, resume_text],
            outputs=[results_section, results_display, process_btn]
        )
    
    return demo

if __name__ == "__main__":
    create_rma_interface().launch(server_name="0.0.0.0", server_port=7899, share=True)