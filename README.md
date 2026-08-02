# Postdoc-application-generator
Generate cover letters, research statements, teaching statements for postdoc application.

这是一个帮你自动撰写博士后申请文书的桌面应用程序。你只需提供招聘信息网址和你的简历，它就能利用人工智能（DeepSeek API）为你生成求职信（Cover Letter）、研究陈述（Research Statement） 或 教学陈述（Teaching Statement），并且支持中英文双语。

主要功能
智能抓取：输入招聘网页链接，程序自动提取职位描述。
多文档类型：一键生成求职信、研究陈述、教学陈述。
双语支持：可选择输出中文或英文。
补充材料：可额外上传论文、毕业论文、教学评估等文件，让生成内容更贴合你的个人背景。
批量处理：支持同时输入多个网址，一次生成所有学校的文书，并打包成 ZIP 文件下载。
本地运行：所有数据只在你的电脑上处理，保护隐私。

如何安装和使用

第一步：安装 Python 环境
访问 python.org，下载并安装 Python 3.8 或更高版本（安装时务必勾选 “Add Python to PATH”）。
安装完成后，打开 PowerShell（或命令提示符），输入 python --version 检查是否安装成功。

第二步：下载本项目代码
点击本仓库右上角的 “Code” → “Download ZIP”，解压到你的电脑文件夹中。
或者使用 Git 克隆（如果你熟悉 Git）。

第三步：安装依赖库
在 PowerShell 中，切换到项目文件夹（例如 cd E:\Cover_letter_generator），然后运行：
    python -m pip install -r requirements.txt
如果 requirements.txt 未提供，请手动安装：
    python -m pip install streamlit openai requests PyPDF2 python-dotenv beautifulsoup4 python-docx

第四步：获取 DeepSeek API Key
注册 DeepSeek 开放平台 账号。
在平台中创建 API Key（以 sk- 开头），并复制保存。
在项目文件夹中创建一个名为 .env 的文件（注意文件名以点开头），用记事本打开，输入：
    DEEPSEEK_API_KEY="你的API密钥"
保存。

第五步：运行程序
在 PowerShell 中，输入：
    python -m streamlit run app.py
程序会自动打开浏览器，显示操作界面。

第六步：开始使用
上传简历（PDF 格式）。
选择文档类型（求职信/研究陈述/教学陈述）。
选择语言（中文/英文）。
输入招聘网址（每行一个，可批量）。
（可选）在“补充材料”中填写额外说明或上传相关文件。
点击 “生成文档”，等待 AI 完成撰写。
生成后，你可以预览第一个文档，并点击按钮下载所有文档的 ZIP 压缩包。

常见问题

Q: 我没有编程经验，能用吗？
A: 可以。只要按步骤安装 Python 和依赖库，然后运行一条命令即可。界面是网页形式，操作直观。

Q: 生成的内容可以直接使用吗？
A: 生成的是框架草稿，建议你根据个人情况进行修改和润色，使其更符合你的风格和经历。

Q: 抓取网页失败怎么办？
A: 如果自动抓取不成功，程序会提示你手动将职位描述粘贴到“备选”文本框中。

Q: 我的 API Key 安全吗？
A: 你的 Key 保存在本地的 .env 文件中，不会被上传到任何地方。注意不要将该文件分享或上传到公开仓库。

依赖库说明

streamlit – 构建用户界面
openai – 调用 DeepSeek API
requests – 抓取网页
PyPDF2 – 解析 PDF 简历
beautifulsoup4 – 解析 HTML
python-docx – 读取 Word 文档
python-dotenv – 管理环境变量

贡献

欢迎提出改进建议或提交 Pull Request。如果你遇到问题，请在 Issues 中反馈。

许可证

本项目采用 MIT 许可证，可自由使用和修改。
