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
      console.error('Error fetching the markdown file:', error);
      document.querySelector('.container').innerHTML = '<p>Error loading content.</p>';
    });
}

function markdownToHtml(markdown) {
  // Convert headers
  markdown = markdown.replace(/^(#{1,6})\s+(.*)$/gm, (match, hashes, title) => {
      return `<h${hashes.length}>${title.trim()}</h${hashes.length}>`;
  });

  // Convert bold text
  markdown = markdown.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Convert italic text
  markdown = markdown.replace(/_(.*?)_/g, '<em>$1</em>');

  // Convert links
  markdown = markdown.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>');

  // Convert unordered lists and properly nest them
  markdown = markdown.replace(/^\s*[\-\+]\s+(.*)/gm, '<li>$1</li>');
  markdown = markdown.replace(/(<li>[\s\S]*?<\/li>)/gm, '<ul>$1</ul>');
  
  // Correct repeated <ul> tags that occur due to consecutive list items
  markdown = markdown.replace(/<\/ul><ul>/gm, '');

  // Convert horizontal rules
  markdown = markdown.replace(/^\s*\-\-\-\s*$/gm, '<hr>');

  // Wrap paragraphs around lines that aren't part of a block element
  markdown = markdown.replace(/^(?!<h|<ul|<li|<\/ul|<a|<em|<strong|<hr>)([\s\S]+?)$/gm, (match) => `<p>${match.trim()}</p>`);

  // Remove paragraphs inadvertently wrapped around list blocks
  markdown = markdown.replace(/<p>(<ul>[\s\S]*?<\/ul>)<\/p>/gm, '$1');

  // Convert inline code
  markdown = markdown.replace(/`(.*?)`/g, '<code>$1</code>');

  // Convert blockquotes
  markdown = markdown.replace(/^>\s+(.*)/gm, '<blockquote>$1</blockquote>');

  // Convert ordered lists
  markdown = markdown.replace(/^\s*\d+\.\s+(.*)/gm, '<li>$1</li>');
  markdown = markdown.replace(/(<li>[\s\S]*?<\/li>)/gm, '<ol>$1</ol>');
  
  // Correct repeated <ol> tags that occur due to consecutive list items
  markdown = markdown.replace(/<\/ol><ol>/gm, '');

  return markdown;
}

