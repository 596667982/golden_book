import katex from 'katex'
import 'katex/dist/katex.min.css'
import type { Directive } from 'vue'

function renderMath(el: HTMLElement, text: string) {
  if (!text) {
    el.innerHTML = ''
    return
  }

  let html = text
  const parts: Array<{ type: 'text' | 'math', content: string, display?: boolean }> = []
  let lastIndex = 0

  // Find all math expressions
  const mathRegex = /\$\$([^\$]+?)\$\$|\$([^\$]+?)\$/g
  let match

  while ((match = mathRegex.exec(text)) !== null) {
    // Add text before math
    if (match.index > lastIndex) {
      parts.push({ type: 'text', content: text.slice(lastIndex, match.index) })
    }

    // Add math expression
    const formula = match[1] || match[2]
    const isDisplay = !!match[1]
    parts.push({ type: 'math', content: formula, display: isDisplay })

    lastIndex = match.index + match[0].length
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push({ type: 'text', content: text.slice(lastIndex) })
  }

  // Render parts
  if (parts.length === 0) {
    el.textContent = text
    return
  }

  html = parts.map(part => {
    if (part.type === 'text') {
      return part.content
    } else {
      try {
        return katex.renderToString(part.content.trim(), {
          displayMode: part.display,
          throwOnError: false
        })
      } catch (e) {
        return part.display ? `$$${part.content}$$` : `$${part.content}$`
      }
    }
  }).join('')

  el.innerHTML = html
}

export const vMath: Directive<HTMLElement, string> = {
  mounted(el, binding) {
    renderMath(el, binding.value)
  },
  updated(el, binding) {
    if (binding.value !== binding.oldValue) {
      renderMath(el, binding.value)
    }
  }
}
