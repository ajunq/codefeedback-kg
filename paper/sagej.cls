%% =========================================================================
%% sagej.cls  —  SHIM LOCAL (no es la clase oficial de SAGE)
%% -------------------------------------------------------------------------
%% Clase de COMPATIBILIDAD basada en `article` para poder compilar el paper
%% en cualquier Overleaf/TeX Live SIN los ficheros propietarios de SAGE
%% (sagej.cls real ni SageV.bst). Define las macros de portada que usa el
%% documento (\runninghead, \affilnum, \affiliation, \corrauth, \email,
%% \keywords) y redirige \bibliographystyle{SageV} a un estilo numerado
%% estándar (unsrtnat), que sí está en toda distribución.
%%
%% USO: sube ESTE fichero a tu proyecto de Overleaf, junto a main.tex,
%% references.bib y la carpeta figs/. Compila con pdfLaTeX. No necesitas
%% ningún otro fichero de SAGE.
%%
%% IMPORTANTE: para el envío FINAL a la revista usa la clase sagej OFICIAL
%% (plantilla SAGE en Overleaf); este shim es solo para obtener un PDF
%% legible con el contenido ya reconciliado. El texto NO se modifica.
%% Generado por Claude Code (agente IA), 2026-06-20.
%% =========================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{sagej}[2026/06/20 v1.0 Shim local de sagej basado en article]

%% Ignorar silenciosamente las opciones de SAGE (sageh, sagev, timesnewroman, ...)
\DeclareOption*{}
\ProcessOptions\relax
\LoadClass[11pt,a4paper]{article}

%% --- Paquetes base que la clase real proporcionaría ---------------------
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[a4paper,margin=2.6cm]{geometry}
\RequirePackage{graphicx}
\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{booktabs}
\RequirePackage{url}
\RequirePackage{etoolbox}
\RequirePackage[numbers,sort&compress]{natbib}
\RequirePackage[hidelinks]{hyperref}

%% --- Bibliografía: forzar estilo numerado estándar (evita SageV.bst) -----
%% Captura la \bibliographystyle de natbib y la redirige a unsrtnat,
%% de modo que \bibliographystyle{SageV} del documento use unsrtnat.bst.
\let\sage@origbibstyle\bibliographystyle
\renewcommand{\bibliographystyle}[1]{\sage@origbibstyle{unsrtnat}}

%% --- Almacenes de portada -----------------------------------------------
\newcommand{\sage@affiliation}{}
\newcommand{\sage@corrauth}{}
\newcommand{\sage@email}{}

%% --- Macros propias de sagej (versión mínima) ---------------------------
\newcommand{\runninghead}[1]{\markboth{#1}{#1}}
\newcommand{\affilnum}[1]{\textsuperscript{#1}}
\providecommand{\affiliation}{}
\renewcommand{\affiliation}[1]{\renewcommand{\sage@affiliation}{#1}}
\providecommand{\corrauth}{}
\renewcommand{\corrauth}[1]{\renewcommand{\sage@corrauth}{#1}}
\providecommand{\email}{}
\renewcommand{\email}[1]{\renewcommand{\sage@email}{#1}}
\newcommand{\keywords}[1]{%
  \par\vskip 0.6em\noindent{\small\textbf{Keywords:} #1}\par\vskip 0.4em}

%% --- Portada propia (self-contained, no usa el \@maketitle de article) ---
\newif\ifsage@titledone
\sage@titledonefalse
\renewcommand{\maketitle}{%
  \ifsage@titledone\else
    \begin{center}%
      {\LARGE\bfseries\@title\par}%
      \vskip 1.0em
      {\large\@author\par}%
      \ifdefempty{\sage@affiliation}{}{\vskip 0.5em{\normalsize\sage@affiliation\par}}%
    \end{center}%
    \ifdefempty{\sage@corrauth}{}{%
      \vskip 0.5em\noindent{\small\textbf{Corresponding author:} \sage@corrauth%
      \ifdefempty{\sage@email}{}{\ \texttt{\sage@email}}\par}}%
    \vskip 1.2em
    \global\sage@titledonetrue
  \fi}

%% El documento coloca \begin{abstract} ANTES de \maketitle (estilo sagej):
%% disparamos la portada justo antes del resumen para conservar el orden
%% correcto (título, autores, resumen, keywords). El \maketitle explícito
%% posterior queda neutralizado por la guarda \ifsage@titledone.
\AtBeginEnvironment{abstract}{\maketitle}

\endinput
