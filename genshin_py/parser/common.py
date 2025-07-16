import re

from bs4 import BeautifulSoup


def parse_html_content(html_text: str, length_limit: int = 500) -> str:
    """Remove the tags from the html content, leaving only the plain text

    ------
    Parameters
    html_text `str`: original html content
    length_limit `int`: limit the maximum length of the returned string
    ------
    Returns
    `str`: plain text without html tags
    """
    # 移除米哈遊自訂的時間標籤
    html_text = html_text.replace('&lt;t class="t_lc"&gt;', "")
    html_text = html_text.replace('&lt;t class="t_gl"&gt;', "")
    html_text = html_text.replace("&lt;/t&gt;", "")

    soup = BeautifulSoup(html_text, features="html.parser")
    url_pattern = re.compile(r"\(\'(https?://.*)\'\)")

    result = ""
    text_length = 0  # 用來統計已處理的文字長度
    for row in soup:
        if text_length > length_limit:
            return result + "..."

        if row.a is not None and (url := url_pattern.search(row.a["href"])):
            # Convert the link to discord format
            result += f"[{row.text}]({url.group(1)})\n"
            text_length += len(row.text)
        elif row.img is not None:
            # Display images as links
            url = row.img["src"]
            result += f"[>>picture<<]({url})\n"
        elif row.name == "div" and row.table is not None:
            # Separate the contents of the same row of the table with symbols
            for tr in row.find_all("tr"):
                for td in tr.find_all("td"):
                    result += "· " + td.text + " "
                    text_length += len(td.text)
                result += "\n"
        elif row.name == "ol":
            # Add numbers to the beginning of each line of ordered items
            for i, li in enumerate(row.find_all("li")):
                result += f"{i+1}. {li.text}\n"
                text_length += len(li.text)
        elif row.name == "ul":  # Unordered items
            # Add a symbol to the beginning of each line of unordered items
            for li in row.find_all("li"):
                result += "· " + li.text + "\n"
                text_length += len(li.text)
        else:  # 一General Content
            text = row.text.strip() + "\n"
            result += text
            text_length += len(text)

    return result
