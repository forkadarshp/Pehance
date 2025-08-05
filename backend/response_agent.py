import re
import json
from typing import Dict, Any, List, Optional
from enum import Enum
import html
import markdown
from agents_framework import Agent, Runner
from enhanced_agents import select_model_for_task, rate_limited_request

class OutputFormat(Enum):
    """Supported output formats"""
    RICH_TEXT = "rich_text"
    CODE_BLOCKS = "code_blocks" 
    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"
    AUTO_DETECT = "auto_detect"

class ResponseFormatResult:
    """Result of response formatting operation"""
    def __init__(self, formatted_content: str, detected_format: OutputFormat, 
                 metadata: Dict[str, Any] = None, code_blocks: List[Dict] = None):
        self.formatted_content = formatted_content
        self.detected_format = detected_format
        self.metadata = metadata or {}
        self.code_blocks = code_blocks or []

class ResponseAgent:
    """Specialized agent for formatting and standardizing output responses"""
    
    @staticmethod
    async def format_response(content: str, target_format: OutputFormat = OutputFormat.AUTO_DETECT, 
                            enhance_quality: bool = True) -> ResponseFormatResult:
        """
        Format response content according to specified format
        
        Args:
            content: Raw content to format
            target_format: Desired output format
            enhance_quality: Whether to enhance content quality during formatting
            
        Returns:
            ResponseFormatResult with formatted content and metadata
        """
        try:
            # Auto-detect format if requested
            if target_format == OutputFormat.AUTO_DETECT:
                target_format = ResponseAgent._auto_detect_format(content)
            
            print(f"📝 Formatting response as: {target_format.value}")
            
            # Apply format-specific processing
            if target_format == OutputFormat.RICH_TEXT:
                return await ResponseAgent._format_as_rich_text(content, enhance_quality)
            elif target_format == OutputFormat.CODE_BLOCKS:
                return await ResponseAgent._format_as_code_blocks(content, enhance_quality)
            elif target_format == OutputFormat.MARKDOWN:
                return await ResponseAgent._format_as_markdown(content, enhance_quality)
            else:  # PLAIN_TEXT
                return ResponseAgent._format_as_plain_text(content)
                
        except Exception as e:
            print(f"❌ Response formatting failed: {e}")
            # Return original content as fallback
            return ResponseFormatResult(
                formatted_content=content,
                detected_format=OutputFormat.PLAIN_TEXT,
                metadata={"error": str(e), "fallback": True}
            )
    
    @staticmethod
    def _auto_detect_format(content: str) -> OutputFormat:
        """Auto-detect the most appropriate format for the content"""
        content_lower = content.lower()
        
        # Count indicators for different formats
        code_indicators = len(re.findall(r'```|`[^`]+`|function|class|def |import |from |#include|<html|<div|<script', content))
        markdown_indicators = len(re.findall(r'#+\s|^\*\s|\*\*[^*]+\*\*|^\d+\.\s|^\-\s', content, re.MULTILINE))
        rich_text_indicators = len(re.findall(r'<[^>]+>|&[a-z]+;', content))
        
        # Decision logic
        if code_indicators >= 3:
            return OutputFormat.CODE_BLOCKS
        elif rich_text_indicators >= 2:
            return OutputFormat.RICH_TEXT
        elif markdown_indicators >= 3:
            return OutputFormat.MARKDOWN
        else:
            # Default decision based on content characteristics
            if len(content) > 1000 and '\n\n' in content:
                return OutputFormat.MARKDOWN  # Long structured content
            elif any(word in content_lower for word in ['step', 'tutorial', 'guide', 'how to']):
                return OutputFormat.RICH_TEXT  # Instructional content
            else:
                return OutputFormat.PLAIN_TEXT
    
    @staticmethod
    async def _format_as_rich_text(content: str, enhance_quality: bool) -> ResponseFormatResult:
        """Format content as rich text with HTML styling"""
        try:
            if enhance_quality:
                # Use AI to enhance and structure the content for rich text
                model = await select_model_for_task("enhancement", 0.6, "content_formatter")
                
                enhancement_agent = Agent(
                    name="Rich Text Formatter",
                    instructions="""You are a professional content formatter specializing in rich text output. Transform the provided content into well-structured, visually appealing rich text format.

**RICH TEXT FORMATTING GUIDELINES:**

**Structure Enhancement:**
- Add clear headings and subheadings using proper hierarchy
- Create logical sections and paragraphs
- Use bullet points and numbered lists where appropriate
- Add emphasis through bold and italic text
- Include line breaks and spacing for readability

**Visual Elements:**
- Use **bold** for important concepts and key points
- Use *italic* for emphasis and quotes
- Create clear section dividers
- Add bullet points (•) for lists
- Use numbered lists for sequential steps

**Content Organization:**
- Start with a brief overview if the content is long
- Group related information together
- Use consistent formatting throughout
- Add transitions between sections
- Include a summary or conclusion if appropriate

**Quality Enhancements:**
- Improve clarity and readability
- Fix any grammatical issues
- Ensure consistent tone and style
- Add context where needed
- Remove redundancy

**OUTPUT FORMAT:**
Return the content formatted as rich text with proper structure, emphasis, and organization. Use standard text formatting (no HTML tags) but structure it clearly with headings, bullet points, and proper emphasis markers.

**CRITICAL:** Focus on making the content scannable, professional, and easy to read while preserving all original information and intent.""",
                    model=model
                )
                
                result = await rate_limited_request(Runner.run, enhancement_agent, content)
                enhanced_content = result.final_output
            else:
                enhanced_content = content
            
            # Convert to HTML with rich formatting
            html_content = ResponseAgent._convert_to_html(enhanced_content)
            
            return ResponseFormatResult(
                formatted_content=html_content,
                detected_format=OutputFormat.RICH_TEXT,
                metadata={
                    "enhanced": enhance_quality,
                    "format_type": "html",
                    "original_length": len(content),
                    "formatted_length": len(html_content)
                }
            )
            
        except Exception as e:
            print(f"❌ Rich text formatting failed: {e}")
            # Fallback to basic HTML conversion
            return ResponseFormatResult(
                formatted_content=ResponseAgent._convert_to_html(content),
                detected_format=OutputFormat.RICH_TEXT,
                metadata={"error": str(e), "fallback": True}
            )
    
    @staticmethod
    async def _format_as_code_blocks(content: str, enhance_quality: bool) -> ResponseFormatResult:
        """Format content with proper code blocks and syntax highlighting"""
        try:
            if enhance_quality:
                # Use AI to identify and properly format code sections
                model = await select_model_for_task("technical", 0.7, "code_formatter")
                
                code_enhancement_agent = Agent(
                    name="Code Block Formatter",
                    instructions="""You are a technical content formatter specializing in code presentation. Transform the provided content to properly highlight and structure code elements.

**CODE FORMATTING GUIDELINES:**

**Code Identification:**
- Identify all code snippets, functions, commands, and technical syntax
- Recognize different programming languages and mark them appropriately
- Distinguish between inline code and code blocks
- Identify configuration files, JSON, XML, and other structured data

**Code Block Formatting:**
- Wrap multi-line code in proper code blocks with language specification
- Use backticks for inline code elements
- Add language identifiers for syntax highlighting (python, javascript, bash, json, etc.)
- Preserve indentation and formatting within code blocks
- Group related code snippets together

**Structure Enhancement:**
- Add clear headings for different code sections
- Provide context and explanations before code blocks
- Include comments within code where helpful
- Add descriptive labels for each code block
- Create logical flow from explanation to implementation

**Technical Documentation:**
- Add setup/installation instructions if relevant
- Include usage examples and expected outputs
- Mention requirements, dependencies, or prerequisites
- Add error handling examples where appropriate
- Include testing or verification steps

**Copy-Friendly Format:**
- Ensure code blocks are easily selectable
- Remove unnecessary line numbers from copyable code
- Keep commands and code snippets clean and executable
- Provide both formatted presentation and raw copyable versions

**OUTPUT FORMAT:**
Return content with properly formatted code blocks using markdown syntax:
```language
code here
```

Include clear explanations, proper code organization, and ensure all technical content is properly highlighted and easily copyable.""",
                    model=model
                )
                
                result = await rate_limited_request(Runner.run, code_enhancement_agent, content)
                enhanced_content = result.final_output
            else:
                enhanced_content = content
            
            # Extract and process code blocks
            code_blocks = ResponseAgent._extract_code_blocks(enhanced_content)
            formatted_content = ResponseAgent._format_code_blocks_html(enhanced_content, code_blocks)
            
            return ResponseFormatResult(
                formatted_content=formatted_content,
                detected_format=OutputFormat.CODE_BLOCKS,
                code_blocks=code_blocks,
                metadata={
                    "enhanced": enhance_quality,
                    "code_blocks_count": len(code_blocks),
                    "languages_detected": list(set(block.get('language', '') for block in code_blocks)),
                    "format_type": "code_enhanced_html"
                }
            )
            
        except Exception as e:
            print(f"❌ Code block formatting failed: {e}")
            # Fallback to basic code formatting
            code_blocks = ResponseAgent._extract_code_blocks(content)
            return ResponseFormatResult(
                formatted_content=ResponseAgent._format_code_blocks_html(content, code_blocks),
                detected_format=OutputFormat.CODE_BLOCKS,
                code_blocks=code_blocks,
                metadata={"error": str(e), "fallback": True}
            )
    
    @staticmethod
    async def _format_as_markdown(content: str, enhance_quality: bool) -> ResponseFormatResult:
        """Format content as proper markdown"""
        try:
            if enhance_quality:
                # Use AI to enhance markdown structure
                model = await select_model_for_task("enhancement", 0.5, "markdown_formatter")
                
                markdown_agent = Agent(
                    name="Markdown Formatter",
                    instructions="""You are a markdown formatting specialist. Transform the provided content into clean, well-structured markdown format.

**MARKDOWN FORMATTING GUIDELINES:**

**Structure Elements:**
- Use proper heading hierarchy (# ## ### ####)
- Create clear sections with appropriate headings
- Use horizontal rules (---) to separate major sections
- Implement proper list formatting (- for bullets, 1. for numbers)
- Add line breaks and spacing for readability

**Text Formatting:**
- Use **bold** for emphasis and important points
- Use *italic* for secondary emphasis and quotes
- Use `inline code` for technical terms and commands
- Create code blocks with proper language specification
- Use > for blockquotes when appropriate

**Advanced Elements:**
- Create tables when data is structured
- Add links in proper markdown format [text](url)
- Use task lists - [ ] and - [x] when appropriate
- Include badges or shields if relevant
- Add proper image references if mentioned

**Content Organization:**
- Start with a clear title or overview
- Group related information under sections
- Use consistent formatting throughout
- Add table of contents for long documents
- Include summary or conclusion sections

**Quality Standards:**
- Ensure all markdown syntax is valid
- Use consistent spacing and indentation
- Make content easily scannable
- Preserve all original information
- Improve clarity and flow

**OUTPUT FORMAT:**
Return properly formatted markdown with clean syntax, logical structure, and professional presentation. Ensure compatibility with standard markdown parsers.""",
                    model=model
                )
                
                result = await rate_limited_request(Runner.run, markdown_agent, content)
                enhanced_content = result.final_output
            else:
                enhanced_content = content
            
            # Convert markdown to HTML for display while preserving markdown
            html_content = markdown.markdown(enhanced_content, extensions=['codehilite', 'fenced_code', 'tables'])
            
            return ResponseFormatResult(
                formatted_content=html_content,
                detected_format=OutputFormat.MARKDOWN,
                metadata={
                    "enhanced": enhance_quality,
                    "format_type": "markdown_to_html",
                    "raw_markdown": enhanced_content,
                    "markdown_length": len(enhanced_content)
                }
            )
            
        except Exception as e:
            print(f"❌ Markdown formatting failed: {e}")
            # Fallback to basic markdown conversion
            html_content = markdown.markdown(content)
            return ResponseFormatResult(
                formatted_content=html_content,
                detected_format=OutputFormat.MARKDOWN,
                metadata={"error": str(e), "fallback": True, "raw_markdown": content}
            )
    
    @staticmethod
    def _format_as_plain_text(content: str) -> ResponseFormatResult:
        """Format content as clean plain text"""
        # Basic text cleaning and formatting
        cleaned_content = re.sub(r'\n{3,}', '\n\n', content)  # Remove excessive line breaks
        cleaned_content = re.sub(r'[ \t]+', ' ', cleaned_content)  # Normalize spaces
        cleaned_content = cleaned_content.strip()
        
        return ResponseFormatResult(
            formatted_content=cleaned_content,
            detected_format=OutputFormat.PLAIN_TEXT,
            metadata={"format_type": "plain_text", "cleaned": True}
        )
    
    @staticmethod
    def _convert_to_html(content: str) -> str:
        """Convert text content to HTML with basic formatting"""
        # Escape HTML characters
        html_content = html.escape(content)
        
        # Convert markdown-style formatting to HTML
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)  # Bold
        html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)  # Italic
        html_content = re.sub(r'`(.*?)`', r'<code>\1</code>', html_content)  # Inline code
        
        # Convert line breaks to HTML
        html_content = html_content.replace('\n\n', '</p><p>')  # Paragraphs
        html_content = html_content.replace('\n', '<br>')  # Line breaks
        html_content = f'<p>{html_content}</p>'
        
        # Handle lists
        html_content = re.sub(r'<p>([•\-\*])\s*(.*?)</p>', r'<ul><li>\2</li></ul>', html_content)
        html_content = re.sub(r'<p>(\d+\.)\s*(.*?)</p>', r'<ol><li>\2</li></ol>', html_content)
        
        return html_content
    
    @staticmethod
    def _extract_code_blocks(content: str) -> List[Dict]:
        """Extract code blocks from content"""
        code_blocks = []
        
        # Find fenced code blocks
        fenced_pattern = r'```(\w+)?\n?(.*?)```'
        matches = re.finditer(fenced_pattern, content, re.DOTALL)
        
        for i, match in enumerate(matches):
            language = match.group(1) or 'text'
            code = match.group(2).strip()
            
            code_blocks.append({
                'id': f'code-block-{i}',
                'language': language,
                'code': code,
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        # Find inline code
        inline_pattern = r'`([^`]+)`'
        inline_matches = re.finditer(inline_pattern, content)
        
        for i, match in enumerate(inline_matches):
            code_blocks.append({
                'id': f'inline-code-{i}',
                'language': 'text',
                'code': match.group(1),
                'inline': True,
                'start_pos': match.start(),
                'end_pos': match.end()
            })
        
        return code_blocks
    
    @staticmethod
    def _format_code_blocks_html(content: str, code_blocks: List[Dict]) -> str:
        """Format content with enhanced code blocks and copy buttons"""
        formatted_content = content
        
        # Replace fenced code blocks with enhanced HTML
        for block in sorted(code_blocks, key=lambda x: x['start_pos'], reverse=True):
            if not block.get('inline', False):
                original_block = f"```{block['language']}\n{block['code']}```"
                
                html_replacement = f'''
<div class="code-block-container" data-language="{block['language']}">
    <div class="code-block-header">
        <span class="language-label">{block['language'].upper()}</span>
        <button class="copy-code-btn" data-code-id="{block['id']}" onclick="copyCodeBlock('{block['id']}')">
            <span class="copy-icon">📋</span>
            <span class="copy-text">Copy</span>
        </button>
    </div>
    <pre class="code-block"><code class="language-{block['language']}" id="{block['id']}">{html.escape(block['code'])}</code></pre>
</div>'''
                
                # Replace the original code block
                formatted_content = formatted_content.replace(original_block, html_replacement)
        
        # Add JavaScript for copy functionality
        formatted_content += '''
<script>
function copyCodeBlock(codeId) {
    const codeElement = document.getElementById(codeId);
    const text = codeElement.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        const button = document.querySelector(`[data-code-id="${codeId}"]`);
        const originalText = button.querySelector('.copy-text').textContent;
        button.querySelector('.copy-text').textContent = 'Copied!';
        button.querySelector('.copy-icon').textContent = '✅';
        
        setTimeout(() => {
            button.querySelector('.copy-text').textContent = originalText;
            button.querySelector('.copy-icon').textContent = '📋';
        }, 2000);
    }).catch(err => {
        console.error('Copy failed:', err);
    });
}
</script>

<style>
.code-block-container {
    margin: 16px 0;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    overflow: hidden;
    background: #f9fafb;
}

.code-block-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background: #f3f4f6;
    border-bottom: 1px solid #e5e7eb;
}

.language-label {
    font-size: 12px;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
}

.copy-code-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    color: #374151;
    transition: all 0.2s;
}

.copy-code-btn:hover {
    background: #f9fafb;
    border-color: #9ca3af;
}

.code-block {
    margin: 0;
    padding: 16px;
    background: #ffffff;
    overflow-x: auto;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 14px;
    line-height: 1.5;
}

.code-block code {
    background: none;
    padding: 0;
    border: none;
    font-family: inherit;
}
</style>'''
        
        return formatted_content

# Factory functions for easy import
async def format_response(content: str, target_format: str = "auto_detect", 
                         enhance_quality: bool = True) -> ResponseFormatResult:
    """
    Main entry point for response formatting
    
    Args:
        content: Content to format
        target_format: Target format (auto_detect, rich_text, code_blocks, markdown, plain_text)
        enhance_quality: Whether to enhance content quality
        
    Returns:
        ResponseFormatResult with formatted content
    """
    format_enum = OutputFormat(target_format)
    return await ResponseAgent.format_response(content, format_enum, enhance_quality)

def detect_content_format(content: str) -> str:
    """Detect the most appropriate format for content"""
    detected = ResponseAgent._auto_detect_format(content)
    return detected.value