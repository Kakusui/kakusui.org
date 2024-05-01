function loadMarkdown(url) {
  fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.text();
    })
    .then(text => {
      document.querySelector('.container').innerHTML = markdownToHtml(text);
    })
    .catch(error => {
      console.error('Error fetching or parsing the markdown file:', error);
      document.querySelector('.container').innerHTML = '<p>Error loading content.</p>';
    });
}

function markdownToHtml(markdown) {
  // Convert headers
  markdown = markdown.replace(/^(#{1,6})\s+(.*?)$/gm, (match, hashes, title) => {
    return `<h${hashes.length}>${title.trim()}</h${hashes.length}>`;
  });

  // Convert bold text
  markdown = markdown.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Convert italic text
  markdown = markdown.replace(/_(.*?)_/g, '<em>$1</em>');

  // Convert links
  markdown = markdown.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>');

  // Convert unordered lists and properly nest them
  markdown = markdown.replace(/^\s*[\-\+\*]\s+(.*)/gm, '<li>$1</li>');
  markdown = markdown.replace(/(<li>.*?<\/li>)/gm, '<ul>$1</ul>');
  markdown = markdown.replace(/<\/ul><ul>/gm, '');

  // Convert horizontal rules
  markdown = markdown.replace(/^\s*---\s*$/gm, '<hr>');

  // Wrap paragraphs around lines that aren't part of a block element
  markdown = markdown.replace(/^(?!<h|<ul|<li|<\/ul|<a|<em|<strong|<hr|<code|<blockquote|<ol>)(.*?)$/gm, (match) => `<p>${match.trim()}</p>`);
  markdown = markdown.replace(/<p>(<ul>.*?<\/ul>)<\/p>/gm, '$1');

  // Convert inline code
  markdown = markdown.replace(/`(.*?)`/g, '<code>$1</code>');

  // Convert blockquotes
  markdown = markdown.replace(/^>\s+(.*)/gm, '<blockquote>$1</blockquote>');

  // Convert ordered lists
// Convert ordered lists
markdown = markdown.replace(/^(\d+)\.\s+(.*)/gm, (match, number, content) => {
  return `<li value="${number}">${content.trim()}</li>`;
});
markdown = markdown.replace(/(<li\s+value="\d+">.*?<\/li>)/gm, '<ol>$1</ol>');
markdown = markdown.replace(/<\/ol><ol>/gm, '');

  // Handle nested lists
  markdown = markdown.replace(/<ul>\s*<li>\s*<ul>/gm, '<ul><li><ul>');
  markdown = markdown.replace(/<\/ul>\s*<\/li>\s*<\/ul>/gm, '</ul></li></ul>');

  // Handle headers within lists
  markdown = markdown.replace(/<li>\s*<h/gm, '<li><h');
  markdown = markdown.replace(/<\/h>\s*<\/li>/gm, '</h></li>');

  // Handle fenced code blocks
  markdown = markdown.replace(/^```(.*?)\n([\s\S]*?)\n```/gm, (match, lang, code) => {
    return `<pre><code${lang ? ` class="${lang.trim()}"` : ''}>${code.trim()}</code></pre>`;
  });

  // Handle nested blockquotes
  markdown = markdown.replace(/^>\s*(.*?)$/gm, (match, content) => {
    const nestedBlockquotes = content.replace(/^>\s*(.*?)$/gm, (match, nestedContent) => {
      return `<blockquote>${nestedContent.trim()}</blockquote>`;
    });
    return `<blockquote>${nestedBlockquotes.trim()}</blockquote>`;
  });

  return markdown;
}