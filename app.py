import os
import requests
import PyPDF2
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import io
import docx  # python-docx
import zipfile
from urllib.parse import urlparse

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量中读取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")

def extract_school_name(url):
    parsed = urlparse(url)
    # 返回域名的主部分，例如 "jobs.university.edu" -> "university"
    domain = parsed.netloc
    # 去掉 www. 等前缀
    parts = domain.split('.')
    # 如果长度 >= 2，取第一个非通用部分，否则返回整个域名
    if len(parts) >= 2:
        # 如果第一个是 www 或类似，取第二个
        if parts[0] in ['www', 'jobs', 'careers']:
            return parts[1] if len(parts) > 1 else parts[0]
        return parts[0]
    else:
        return domain

def fetch_job_description(url):
    """
    尝试从给定 URL 抓取网页的可见文本。
    如果成功返回文本内容，否则返回 None。
    """
    try:
        # 设置一个常见的 User-Agent，降低被拒的风险
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # 发送 GET 请求，设置超时 10 秒
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 如果状态码不是 200，抛出异常

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 移除 script 和 style 标签内的内容（它们不是可见文本）
        for script in soup(["script", "style"]):
            script.decompose()

        # 获取所有可见文本，用换行符分隔
        text = soup.get_text(separator='\n')

        # 清理多余的空白行
        lines = (line.strip() for line in text.splitlines())
        # 过滤掉空行
        clean_text = '\n'.join(line for line in lines if line)

        return clean_text

    except Exception as e:
        # 任何异常（网络、解析、超时等）都视为抓取失败
        print(f"抓取网页失败: {e}")  # 在后台打印错误，方便调试
        return None

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_uploaded_files(uploaded_files):
    """
    从多个上传文件中提取所有文本，合并为一个字符串。
    支持 .pdf, .docx, .txt
    """
    all_text = ""
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        file_extension = file_name.split('.')[-1].lower()
        
        try:
            if file_extension == "pdf":
                # 使用 PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            elif file_extension == "docx":
                # 使用 python-docx
                doc = docx.Document(io.BytesIO(uploaded_file.read()))
                text = "\n".join([para.text for para in doc.paragraphs])
            elif file_extension == "txt":
                # 直接解码文本（假设 UTF-8）
                text = uploaded_file.read().decode("utf-8", errors="ignore")
            else:
                continue  # 跳过不支持的格式
        except Exception as e:
            st.warning(f"读取文件 {file_name} 失败：{e}")
            continue
        
        # 添加文件头以区分来源
        all_text += f"\n===== 文件：{file_name} =====\n{text}\n"
    
    return all_text

def generate_document(doc_type, job_desc, resume_text, language="中文", extra_text="", extra_files_content=""):
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    # 语言指令
    if language == "English":
        lang_instruction = "You MUST write in English. Use formal academic English."
        # 还可以根据文档类型微调语言风格
    else:
        lang_instruction = "你必须用中文撰写。使用正式、专业的学术中文。"
    
    # 根据文档类型构建不同的提示词
    if doc_type == "Cover Letter":
        doc_name = "求职信"
        doc_name_en = "cover letter"
        specific_instructions = """
        突出申请人的研究经历、技能和成果如何与职位要求相匹配。
        结构清晰，包含开头称呼、正文（2-3段）和结尾敬语。
        """
    elif doc_type == "Research Statement":
        doc_name = "研究陈述"
        doc_name_en = "research statement"
        specific_instructions = """
        重点描述申请人的研究兴趣、过往研究项目、主要贡献和未来研究计划。
        需展示与招聘方向的高度契合，以及潜在的学术影响力。
        结构可包括：研究背景、主要成果、未来方向。
        """
    elif doc_type == "Teaching Statement":
        doc_name = "教学陈述"
        doc_name_en = "teaching statement"
        specific_instructions = """
        阐述申请人的教学理念、过往教学经验、所掌握的教学方法，以及如何针对该职位开展教学。
        强调对学生学习的促进和教学创新能力。
        结构可包括：教学理念、经验与成就、未来教学规划。
        """
    else:
        raise ValueError("Unsupported document type")

        # 构建额外信息部分
    extra_section = ""
    if extra_text.strip():
        extra_section += f"\n申请人提供的补充说明：\n{extra_text}\n"
    if extra_files_content.strip():
        extra_section += f"\n申请人上传的补充文件内容：\n{extra_files_content}\n"
    
    # 根据文档类型构建基础提示词（与之前类似）
    # 但在要求中增加一条：充分利用补充信息
    # 在 prompt 中嵌入 extra_section
    prompt = f"""
    你是一位经验丰富的学术招聘专家。请根据以下职位描述和申请人的简历信息，以及用户补充的信息，为申请人撰写一封专业的、有针对性的{doc_name}。

    包含职位描述的文本，请从中识别出职位描述：
    {job_desc}

    申请人简历：
    {resume_text}

    用户补充的信息：
    {extra_section}

    要求：
    1. {doc_name}需正式、专业，语气诚恳。
    2. {specific_instructions}
    3. 请充分利用用户补充的信息，使文档内容详实、个性化。
    4. {lang_instruction}
    5. 直接输出文档正文，不要包含任何额外的解释或说明。
    """
    
    system_prompt = f"你是一个专业的学术文档撰写助手，擅长撰写{doc_name}。{lang_instruction}"
    
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        stream=False,
        extra_body={"thinking": {"type": "disabled"}},
        timeout=120.0  # 设置超时时间为 120 秒
    )
    return response.choices[0].message.content

# 主界面
st.set_page_config(page_title="AI 博士后求职文档生成器", page_icon="📄")
st.title("📄 AI 博士后求职文档生成器")

# 侧边栏：用于输入 API Key 和招聘信息网址
with st.sidebar:
    st.header("配置信息")
    # 如果你不想用 .env 文件，也可以让用户在界面上输入 Key
    # user_api_key = st.text_input("DeepSeek API Key", type="password")
    job_urls_input = st.text_area(
        "招聘信息网址（每行一个）",
        placeholder="https://university1.edu/job\nhttps://university2.edu/postdoc",
        height=200
    )

# 主界面：用于上传简历和生成求职信
uploaded_file = st.file_uploader("上传你的简历 (PDF格式)", type="pdf")

# 文档类型选择
doc_type = st.radio(
    "选择要生成的文档类型",
    options=["Cover Letter", "Research Statement", "Teaching Statement"],
    index=0  # 默认 Cover Letter
)

# ========== 新增语言选择 ==========
language = st.selectbox(
    "选择语言",
    options=["中文", "English"],
    index=0  # 默认选中“中文”
)
# =================================

job_description = st.text_area("备选，若网站抓取失败，则在此粘贴职位描述 (JD)", height=200)

# 根据文档类型显示额外的输入
with st.expander("📎 补充材料（可选）", expanded=(doc_type == "Research Statement" or doc_type == "Teaching Statement")):
    extra_text = st.text_area(
        "额外研究/教学说明",
        placeholder="你可以输入研究/教学理念、心得体会等...",
        height=150
    )
    
    extra_files = st.file_uploader(
        "上传补充文件（论文、教学评估材料等）",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="支持 PDF, DOCX, TXT 格式，可多选"
    )

if st.button("生成文档"):
    if not api_key:
        st.error("请设置 DeepSeek API Key。")
        st.stop()

    # 1. 解析简历
    resume_text = ""
    if uploaded_file is not None:
        with st.spinner("正在解析简历..."):
            resume_text = extract_text_from_pdf(uploaded_file)
    else:
        st.error("请上传你的简历。")
        st.stop()

    # 获取额外文本和文件
    extra_files_content = ""
    if extra_files:
        with st.spinner("正在读取补充文件..."):
            extra_files_content = extract_text_from_uploaded_files(extra_files)

    # 2. 处理 URL 列表
    urls = [url.strip() for url in job_urls_input.splitlines() if url.strip()]
    if not urls:
        st.error("请至少输入一个有效的招聘信息网址。")
        st.stop()
    
    # 准备生成结果
    results = []  # 存储 (filename, content) 的列表
    progress_bar = st.progress(0, text="开始处理...")
    status_placeholder = st.empty()
    
    total = len(urls)
    for idx, url in enumerate(urls):
        status_placeholder.info(f"正在处理第 {idx+1}/{total} 个学校: {url}")
        
        # 抓取职位描述
        with st.spinner(f"正在抓取 {url} ..."):
            fetched_text = fetch_job_description(url)
            if not fetched_text:
                st.warning(f"抓取 {url} 失败，跳过。")
                progress_bar.progress((idx + 1) / total)
                continue  # 跳过这个 URL
        
        # 使用抓取到的文本作为职位描述（如果用户还手动粘贴了，可以选择合并，但这里我们以抓取为主）
        final_job_desc = fetched_text if fetched_text else job_description  # 如果抓取为空，可回退到手动粘贴，但建议只抓取
        
        # 如果抓取为空，并且用户没有手动粘贴，则跳过
        if not final_job_desc:
            st.warning(f"无法获取职位描述: {url}，请检查网址或手动粘贴。")
            progress_bar.progress((idx + 1) / total)
            continue
        
        # 生成文档（使用相同的文档类型、语言、额外文本和文件）
        with st.spinner(f"正在生成 {doc_type} 文档..."):
            try:
                generated_text = generate_document(
                    doc_type=doc_type,
                    job_desc=final_job_desc,
                    resume_text=resume_text,
                    language=language,
                    extra_text=extra_text,
                    extra_files_content=extra_files_content
                )
            except Exception as e:
                st.error(f"生成失败 ({url}): {e}")
                progress_bar.progress((idx + 1) / total)
                continue
        
        # 构建文件名
        school = extract_school_name(url)
        # 文档类型缩写
        doc_map = {
            "Cover Letter": "CL",
            "Research Statement": "RS",
            "Teaching Statement": "TS"
        }
        doc_abbr = doc_map[doc_type]
        lang_suffix = "en" if language == "English" else "zh"
        filename = f"{school}_{doc_abbr}_{lang_suffix}.txt"
        results.append((filename, generated_text))
        
        # 更新进度
        progress_bar.progress((idx + 1) / total)
    
    status_placeholder.empty()
    progress_bar.empty()
    
    if not results:
        st.error("所有网址处理失败，请检查网络或输入。")
        st.stop()
    
    # 打包成 ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for filename, content in results:
            zip_file.writestr(filename, content)
    zip_buffer.seek(0)
    
    st.success(f"成功生成 {len(results)} 份文档！")
    st.download_button(
        label="📦 下载所有文档 (ZIP 压缩包)",
        data=zip_buffer,
        file_name=f"{doc_type.replace(' ', '_')}_batch_{lang_suffix}.zip",
        mime="application/zip"
    )
    
    # 可选：在界面上预览第一个文档（或全部）
    with st.expander("预览生成的文档（第一个）"):
        if results:
            st.text(results[0][1])  # 展示第一个内容