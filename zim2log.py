import argparse
import os
import re

from bs4 import BeautifulSoup, Tag


def html_to_md(html_content: str, notebook: str):
    html_content = html_content.replace("<i>", "*")
    html_content = html_content.replace("</i>", "*")
    html_content = html_content.replace("<b>", "**")
    html_content = html_content.replace("</b>", "**")

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    soup.find(class_="header").decompose()
    for anchor in soup.find_all(class_="h_anchor"):
        anchor.decompose()

    # Define a function to recursively convert HTML elements to Markdown
    def convert_element(element, list_level=0):
        md = ""
        match element.name:
            case "p":
                for child in element.children:
                    md += convert_element(child, list_level)

            case "h1" | "h2" | "h3" | "h4" | "h5" | "h6":
                md += f"{'#' * int(element.name[1])} {element.get_text()}\n\n"

            case "ul":
                list_level += 1
                list_str = list_level * "\t"
                for li in element.find_all("li", recursive=False):
                    md += f"{list_str}- " + convert_element(li, list_level)
                md += "\n"

            case "ol":
                list_level += 1
                list_str = list_level * "\t"
                for i, li in enumerate(
                    element.find_all("li", recursive=False), start=1
                ):
                    md += convert_element(li, list_level)

                md += "\n"
            case "a":
                title = ""
                if element.has_attr("title"):
                    title = element["title"]

                href = ""
                if element.has_attr("href"):
                    href = element["href"]
                md += f"[{title}]({href})"

            case "img":
                nonlocal notebook
                src = os.path.normpath(os.path.join(notebook, element["src"]))

                title = ""
                if element.has_attr("title"):
                    title = element["title"]

                md += f"![{title}]({src})"

            case "li":
                for child in element.children:
                    md += convert_element(child, list_level)

            case _:
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
    parser = argparse.ArgumentParser(
        description="Convert Zim Desktop Wiki HTML export files into Logseq md."
    )

    parser.add_argument("input_file", type=str, help="Path to the input file")
    parser.add_argument("--output", "-o", type=str, help="Path to the output file")
    parser.add_argument(
        "--notebook",
        "-n",
        type=str,
        help="Path to the original notebook (to interpret local images files paths",
    )

    args = parser.parse_args()

    filename = args.input_file
    with open(filename, "r", encoding="utf-8") as file:
        html_content = file.read()

    filename_out, _ = os.path.splitext(filename)

    markdown_content = html_to_md(html_content, args.notebook)

    with open(filename_out + ".md", "w") as file:
        file.write(markdown_content)
