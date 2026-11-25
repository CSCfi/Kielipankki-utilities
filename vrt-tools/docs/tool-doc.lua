--[[
tool-doc.lua

Pandoc Lua filter for converting the Markdown documentation of VRT
tools (generated with "tool --help-markdown"; see libvrt/mdhelp.py) to
man pages and HTML. Used by make-tool-docs.

For all formats, rewrite links to other tool docs ("tool.md"): for
man, to "tool(1)"; otherwise, to "tool.html".

For man:
- remove the level-1 heading and use it as the title;
- add a NAME section with the summary given as metadata field
  "summary" (Markdown; make-tool-docs passes the first sentence of the
  description), without its final full stop;
- shift headings up by one level and upper-case section headings;
- convert the level-4 headings of options (beginning with inline
  code) and their content to a definition list (tagged paragraphs),
  with option names in bold and argument names in italics.

For HTML, use the level-1 heading as the page title.
]]


local stringify = pandoc.utils.stringify


local function tool_link(link)
  local tool = link.target:match('^([%w._-]+)%.md$')
  if not tool then
    return nil
  end
  if FORMAT == 'man' then
    local ref = pandoc.Inlines{pandoc.Strong{pandoc.Str(tool)},
                               pandoc.Str('(1)')}
    if stringify(link.content) == tool then
      return ref
    end
    return link.content .. pandoc.Inlines{pandoc.Space(), pandoc.Str('(')}
      .. ref .. pandoc.Inlines{pandoc.Str(')')}
  end
  link.target = tool .. '.html'
  return link
end


local function is_option_heading(block)
  return block.t == 'Header' and block.level == 4
    and #block.content > 0 and block.content[1].t == 'Code'
end


-- Return the inlines of an option heading formatted for a man page
local function option_term(inlines)
  local term = pandoc.Inlines{}
  for _, inline in ipairs(inlines) do
    if inline.t == 'Code' then
      local opt, arg = inline.text:match('^(%S+)%s+(.+)$')
      if opt then
        term:extend{pandoc.Strong{pandoc.Str(opt)}, pandoc.Space(),
                    pandoc.Emph{pandoc.Str(arg)}}
      elseif inline.text:match('^%-') then
        term:insert(pandoc.Strong{pandoc.Str(inline.text)})
      else
        -- Positional argument
        term:insert(pandoc.Emph{pandoc.Str(inline.text)})
      end
    else
      term:insert(inline)
    end
  end
  return term
end


local function man_doc(doc)
  local blocks = pandoc.Blocks{}
  local title
  -- Items of the current definition list of options
  local items = nil

  local function flush_items()
    if items then
      blocks:insert(pandoc.DefinitionList(items))
      items = nil
    end
  end

  for _, block in ipairs(doc.blocks) do
    if block.t == 'Header' and block.level == 1 and not title then
      title = stringify(block.content)
    elseif is_option_heading(block) then
      items = items or {}
      table.insert(items, {option_term(block.content), {pandoc.Blocks{}}})
    elseif block.t == 'Header' then
      flush_items()
      local text = stringify(block.content)
      if block.level == 2 then
        block = pandoc.Header(1, pandoc.Inlines(text:upper()))
      else
        block.level = block.level - 1
      end
      blocks:insert(block)
    elseif items then
      items[#items][2][1]:insert(block)
    else
      blocks:insert(block)
    end
  end
  flush_items()

  if title then
    local name = title
    if doc.meta.summary then
      local summary = stringify(pandoc.read(stringify(doc.meta.summary),
                                            'markdown-smart').blocks)
      name = name .. ' - ' .. summary:gsub('%.$', '')
    end
    blocks:insert(1, pandoc.Header(1, pandoc.Inlines('NAME')))
    blocks:insert(2, pandoc.Para(pandoc.Inlines(name)))
    doc.meta.title = doc.meta.title or pandoc.Inlines(title)
  end
  doc.meta.section = doc.meta.section or pandoc.Inlines('1')
  doc.blocks = blocks
  return doc
end


local function html_doc(doc)
  if not doc.meta.pagetitle then
    for _, block in ipairs(doc.blocks) do
      if block.t == 'Header' and block.level == 1 then
        doc.meta.pagetitle = pandoc.Inlines(stringify(block.content))
        break
      end
    end
  end
  return doc
end


return {
  {Link = tool_link},
  {Pandoc = function (doc)
     if FORMAT == 'man' then
       return man_doc(doc)
     elseif FORMAT:match('html') then
       return html_doc(doc)
     end
   end},
}
