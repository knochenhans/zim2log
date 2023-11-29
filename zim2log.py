import re
from bs4 import BeautifulSoup, Tag


def html_to_md(html_content: str):
    html_content = html_content.replace("<i>", "*")
    html_content = html_content.replace("</i>", "*")
    html_content = html_content.replace("<b>", "**")
    html_content = html_content.replace("</b>", "**")

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    soup.find(class_="header").decompose()

    # Define a function to recursively convert HTML elements to Markdown
    def convert_element(element, list_level=0):
        md = ""
        if element.name == "p":
            md += f"{element.get_text()}\n\n"
        elif element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            md += f"{'#' * int(element.name[1])} {element.get_text()}\n\n"
        elif element.name == "ul":
            list_level += 1
            list_str = list_level * "\t"
            for li in element.find_all("li", recursive=False):
                md += f"{list_str}- " + convert_element(li, list_level)
            md += "\n"
        elif element.name == "ol":
            list_level += 1
            list_str = list_level * "\t"
            for i, li in enumerate(element.find_all("li", recursive=False), start=1):
                md += convert_element(li, list_level)
            md += "\n"
        elif element.name == "a":
            md += f"[{element['title']}]({element['href']})"
        elif element.name == "li":
            for child in element.children:
                md += convert_element(child, list_level)
        else:
            if isinstance(element, Tag):
                for child in element.children:
                    md += convert_element(child, list_level)
            else:
                md += element.get_text() + "\n"

        return md

    # Convert the parsed HTML to Markdown
    md_content = ""
    for element in soup.body.children:
        md_content += convert_element(element)

    md_content = re.sub(r"\n{3,}", "\n\n", md_content)

    return md_content

if __name__ == "__main__":
    with open("/tmp/logseq/Akustik.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    markdown_content = html_to_md(html_content)
    print(markdown_content)