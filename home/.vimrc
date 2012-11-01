" have syntax highlighting in terminals which can display colours:
if has('syntax') && (&t_Co > 2)
  syntax on
endif

"Automaically indent when adding a curly bracket, etc.
set smartindent


" Python indentation convention
set shiftwidth=4
set tabstop=4
set expandtab
set smarttab

autocmd FileType make setlocal noexpandtab

filetype on

" Associate some Drupal file extensions with PHP
au BufNewFile,BufRead *.module set filetype=php
au BufNewFile,BufRead *.install set filetype=php
au BufNewFile,BufRead *.test set filetype=php

" Always show the row and col position
set ruler
" Enable incremental search
set incsearch
" Smart ignore case when searching
set smartcase


" Status line
set laststatus=2
set statusline=
set statusline+=%-3.3n\                      " buffer number
set statusline+=%f\                          " filename
set statusline+=%h%m%r%w                     " status flags
set statusline+=\[%{strlen(&ft)?&ft:'none'}] " file type
set statusline+=%=                           " right align remainder
set statusline+=0x%-8B                       " character value
set statusline+=%-14(%l,%c%V%)               " line, character
set statusline+=%<%P                         " file position


" Display incomplete commands.
set showcmd



" Show editing mode
set showmode
