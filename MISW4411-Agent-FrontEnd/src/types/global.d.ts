/**
 * @fileoverview Declaraciones de Tipos Globales
 * 
 * Archivo de declaraciones de tipos globales para TypeScript.
 * Extiende las definiciones de tipos de librerías externas y define
 * tipos personalizados para elementos HTML y SVG.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

/// <reference types="react" />
/// <reference types="react-dom" />
/// <reference types="node" />

/**
 * Declaraciones de tipos para react-helmet-async
 * Extiende los tipos de la librería para mejor integración con TypeScript
 */
declare module 'react-helmet-async' {
  import { ReactNode } from 'react';
  
  export interface HelmetProps {
    children?: ReactNode;
  }
  
  export interface HelmetData {
    title: string;
    meta: Array<{ name: string; content: string }>;
    link: Array<{ rel: string; href: string }>;
  }
  
  export const Helmet: React.FC<HelmetProps>;
  export const HelmetProvider: React.FC<{ children: ReactNode }>;
  export const useHelmet: () => HelmetData;
}

/**
 * Declaraciones de tipos para framer-motion
 * Extiende los tipos de la librería de animaciones para mejor integración
 */
declare module 'framer-motion' {
  import { ReactNode, RefObject } from 'react';
  
  /**
   * Props para componentes de Framer Motion
   * Define las propiedades disponibles para elementos animados
   */
  export interface MotionProps {
    children?: ReactNode;        // Contenido del componente
    ref?: RefObject<any>;        // Referencia al elemento DOM
    initial?: any;               // Estado inicial de la animación
    animate?: any;               // Estado final de la animación
    exit?: any;                  // Estado de salida de la animación
    transition?: any;            // Configuración de la transición
    whileHover?: any;            // Animación al hacer hover
    whileTap?: any;              // Animación al hacer tap
    whileInView?: any;           // Animación al entrar en vista
    viewport?: any;              // Configuración del viewport
    variants?: any;              // Variantes de animación
    className?: string;          // Clases CSS adicionales
    [key: string]: any;          // Propiedades adicionales
  }
  
  export const motion: {
    div: React.FC<MotionProps>;
    section: React.FC<MotionProps>;
    h1: React.FC<MotionProps>;
    h2: React.FC<MotionProps>;
    h3: React.FC<MotionProps>;
    p: React.FC<MotionProps>;
    span: React.FC<MotionProps>;
    a: React.FC<MotionProps>;
    button: React.FC<MotionProps>;
    img: React.FC<MotionProps>;
    [key: string]: React.FC<MotionProps>;
  };
  
  export const AnimatePresence: React.FC<{ children: ReactNode }>;
  export const useMotionValue: <T>(initial: T) => { get: () => T; set: (value: T) => void };
  export const useTransform: (value: any, input: number[], output: number[]) => any;
}

/**
 * Declaraciones de tipos para react-intersection-observer
 * Extiende los tipos de la librería para detección de elementos en vista
 */
declare module 'react-intersection-observer' {
  import { RefObject } from 'react';
  
  /**
   * Opciones para el hook useInView
   * Configuración para el observador de intersección
   */
  export interface UseInViewOptions {
    threshold?: number | number[];    // Umbral de visibilidad (0-1)
    rootMargin?: string;              // Margen del root element
    triggerOnce?: boolean;            // Activar solo una vez
    root?: RefObject<Element>;        // Elemento root para la observación
  }
  
  /**
   * Resultado del hook useInView
   * Estado y datos del elemento observado
   */
  export interface UseInViewResult {
    ref: RefObject<any>;                    // Referencia al elemento observado
    inView: boolean;                        // Indica si el elemento está en vista
    entry?: IntersectionObserverEntry;      // Datos de la intersección
  }

  /**
   * Hook para detectar si un elemento está en vista
   * 
   * @param options - Opciones de configuración del observador
   * @returns Array con [ref, inView, entry]
   */
  export const useInView: (options?: UseInViewOptions) => [RefObject<any>, boolean, IntersectionObserverEntry?];
}

/**
 * Extensión de tipos JSX para elementos HTML y SVG
 * Define tipos personalizados para todos los elementos HTML y SVG
 * utilizados en la aplicación, proporcionando mejor autocompletado
 * y verificación de tipos en JSX
 */
declare namespace JSX {
  /**
   * Elementos intrínsecos de JSX
   * Define las propiedades disponibles para cada elemento HTML/SVG
   */
  interface IntrinsicElements {
    div: React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement>;
    section: React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
    h1: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
    h2: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
    h3: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
    h4: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
    h5: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
    h6: React.DetailedHTMLProps<React.HTMLAttributes<HTMLHeadingElement>, HTMLHeadingElement>;
    p: React.DetailedHTMLProps<React.HTMLAttributes<HTMLParagraphElement>, HTMLParagraphElement>;
    span: React.DetailedHTMLProps<React.HTMLAttributes<HTMLSpanElement>, HTMLSpanElement>;
    a: React.DetailedHTMLProps<React.AnchorHTMLAttributes<HTMLAnchorElement>, HTMLAnchorElement>;
    button: React.DetailedHTMLProps<React.ButtonHTMLAttributes<HTMLButtonElement>, HTMLButtonElement>;
    img: React.DetailedHTMLProps<React.ImgHTMLAttributes<HTMLImageElement>, HTMLImageElement>;
    ul: React.DetailedHTMLProps<React.HTMLAttributes<HTMLUListElement>, HTMLUListElement>;
    ol: React.DetailedHTMLProps<React.HTMLAttributes<HTMLOListElement>, HTMLOListElement>;
    li: React.DetailedHTMLProps<React.HTMLAttributes<HTMLLIElement>, HTMLLIElement>;
    nav: React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
    header: React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
    footer: React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
    main: React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
    article: React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
    aside: React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
    form: React.DetailedHTMLProps<React.FormHTMLAttributes<HTMLFormElement>, HTMLFormElement>;
    input: React.DetailedHTMLProps<React.InputHTMLAttributes<HTMLInputElement>, HTMLInputElement>;
    textarea: React.DetailedHTMLProps<React.TextareaHTMLAttributes<HTMLTextAreaElement>, HTMLTextAreaElement>;
    select: React.DetailedHTMLProps<React.SelectHTMLAttributes<HTMLSelectElement>, HTMLSelectElement>;
    option: React.DetailedHTMLProps<React.OptionHTMLAttributes<HTMLOptionElement>, HTMLOptionElement>;
    label: React.DetailedHTMLProps<React.LabelHTMLAttributes<HTMLLabelElement>, HTMLLabelElement>;
    title: React.DetailedHTMLProps<React.HTMLAttributes<HTMLTitleElement>, HTMLTitleElement>;
    meta: React.DetailedHTMLProps<React.MetaHTMLAttributes<HTMLMetaElement>, HTMLMetaElement>;
    link: React.DetailedHTMLProps<React.LinkHTMLAttributes<HTMLLinkElement>, HTMLLinkElement>;
    script: React.DetailedHTMLProps<React.ScriptHTMLAttributes<HTMLScriptElement>, HTMLScriptElement>;
    style: React.DetailedHTMLProps<React.StyleHTMLAttributes<HTMLStyleElement>, HTMLStyleElement>;
    iframe: React.DetailedHTMLProps<React.IframeHTMLAttributes<HTMLIFrameElement>, HTMLIFrameElement>;
    video: React.DetailedHTMLProps<React.VideoHTMLAttributes<HTMLVideoElement>, HTMLVideoElement>;
    audio: React.DetailedHTMLProps<React.AudioHTMLAttributes<HTMLAudioElement>, HTMLAudioElement>;
    canvas: React.DetailedHTMLProps<React.CanvasHTMLAttributes<HTMLCanvasElement>, HTMLCanvasElement>;
    svg: React.DetailedHTMLProps<React.SVGAttributes<SVGElement>, SVGElement>;
    path: React.DetailedHTMLProps<React.SVGAttributes<SVGPathElement>, SVGPathElement>;
    circle: React.DetailedHTMLProps<React.SVGAttributes<SVGCircleElement>, SVGCircleElement>;
    rect: React.DetailedHTMLProps<React.SVGAttributes<SVGRectElement>, SVGRectElement>;
    line: React.DetailedHTMLProps<React.SVGAttributes<SVGLineElement>, SVGLineElement>;
    polygon: React.DetailedHTMLProps<React.SVGAttributes<SVGPolygonElement>, SVGPolygonElement>;
    polyline: React.DetailedHTMLProps<React.SVGAttributes<SVGPolylineElement>, SVGPolylineElement>;
    ellipse: React.DetailedHTMLProps<React.SVGAttributes<SVGEllipseElement>, SVGEllipseElement>;
    g: React.DetailedHTMLProps<React.SVGAttributes<SVGGElement>, SVGGElement>;
    defs: React.DetailedHTMLProps<React.SVGAttributes<SVGDefsElement>, SVGDefsElement>;
    clipPath: React.DetailedHTMLProps<React.SVGAttributes<SVGClipPathElement>, SVGClipPathElement>;
    linearGradient: React.DetailedHTMLProps<React.SVGAttributes<SVGLinearGradientElement>, SVGLinearGradientElement>;
    radialGradient: React.DetailedHTMLProps<React.SVGAttributes<SVGRadialGradientElement>, SVGRadialGradientElement>;
    stop: React.DetailedHTMLProps<React.SVGAttributes<SVGStopElement>, SVGStopElement>;
    mask: React.DetailedHTMLProps<React.SVGAttributes<SVGMaskElement>, SVGMaskElement>;
    pattern: React.DetailedHTMLProps<React.SVGAttributes<SVGPatternElement>, SVGPatternElement>;
    symbol: React.DetailedHTMLProps<React.SVGAttributes<SVGSymbolElement>, SVGSymbolElement>;
    use: React.DetailedHTMLProps<React.SVGAttributes<SVGUseElement>, SVGUseElement>;
    text: React.DetailedHTMLProps<React.SVGAttributes<SVGTextElement>, SVGTextElement>;
    tspan: React.DetailedHTMLProps<React.SVGAttributes<SVGTSpanElement>, SVGTSpanElement>;
    textPath: React.DetailedHTMLProps<React.SVGAttributes<SVGTextPathElement>, SVGTextPathElement>;
    foreignObject: React.DetailedHTMLProps<React.SVGAttributes<SVGForeignObjectElement>, SVGForeignObjectElement>;
    image: React.DetailedHTMLProps<React.SVGAttributes<SVGImageElement>, SVGImageElement>;
    filter: React.DetailedHTMLProps<React.SVGAttributes<SVGFilterElement>, SVGFilterElement>;
    feGaussianBlur: React.DetailedHTMLProps<React.SVGAttributes<SVGFEGaussianBlurElement>, SVGFEGaussianBlurElement>;
    feOffset: React.DetailedHTMLProps<React.SVGAttributes<SVGFEOffsetElement>, SVGFEOffsetElement>;
    feComposite: React.DetailedHTMLProps<React.SVGAttributes<SVGFECompositeElement>, SVGFECompositeElement>;
    feMerge: React.DetailedHTMLProps<React.SVGAttributes<SVGFEMergeElement>, SVGFEMergeElement>;
    feMergeNode: React.DetailedHTMLProps<React.SVGAttributes<SVGFEMergeNodeElement>, SVGFEMergeNodeElement>;
    feFlood: React.DetailedHTMLProps<React.SVGAttributes<SVGFEFloodElement>, SVGFEFloodElement>;
    feColorMatrix: React.DetailedHTMLProps<React.SVGAttributes<SVGFEColorMatrixElement>, SVGFEColorMatrixElement>;
    feBlend: React.DetailedHTMLProps<React.SVGAttributes<SVGFEBlendElement>, SVGFEBlendElement>;
    feMorphology: React.DetailedHTMLProps<React.SVGAttributes<SVGFEMorphologyElement>, SVGFEMorphologyElement>;
    feConvolveMatrix: React.DetailedHTMLProps<React.SVGAttributes<SVGFEConvolveMatrixElement>, SVGFEConvolveMatrixElement>;
    feDisplacementMap: React.DetailedHTMLProps<React.SVGAttributes<SVGFEDisplacementMapElement>, SVGFEDisplacementMapElement>;
    feTurbulence: React.DetailedHTMLProps<React.SVGAttributes<SVGFETurbulenceElement>, SVGFETurbulenceElement>;
    feSpecularLighting: React.DetailedHTMLProps<React.SVGAttributes<SVGFESpecularLightingElement>, SVGFESpecularLightingElement>;
    feDiffuseLighting: React.DetailedHTMLProps<React.SVGAttributes<SVGFEDiffuseLightingElement>, SVGFEDiffuseLightingElement>;
    fePointLight: React.DetailedHTMLProps<React.SVGAttributes<SVGFEPointLightElement>, SVGFEPointLightElement>;
    feSpotLight: React.DetailedHTMLProps<React.SVGAttributes<SVGFESpotLightElement>, SVGFESpotLightElement>;
    feDistantLight: React.DetailedHTMLProps<React.SVGAttributes<SVGFEDistantLightElement>, SVGFEDistantLightElement>;
    feDropShadow: React.DetailedHTMLProps<React.SVGAttributes<SVGFEDropShadowElement>, SVGFEDropShadowElement>;
    feImage: React.DetailedHTMLProps<React.SVGAttributes<SVGFEImageElement>, SVGFEImageElement>;
    feTile: React.DetailedHTMLProps<React.SVGAttributes<SVGFETileElement>, SVGFETileElement>;
    feFuncR: React.DetailedHTMLProps<React.SVGAttributes<SVGFEFuncRElement>, SVGFEFuncRElement>;
    feFuncG: React.DetailedHTMLProps<React.SVGAttributes<SVGFEFuncGElement>, SVGFEFuncGElement>;
    feFuncB: React.DetailedHTMLProps<React.SVGAttributes<SVGFEFuncBElement>, SVGFEFuncBElement>;
    feFuncA: React.DetailedHTMLProps<React.SVGAttributes<SVGFEFuncAElement>, SVGFEFuncAElement>;
    feComponentTransfer: React.DetailedHTMLProps<React.SVGAttributes<SVGFEComponentTransferElement>, SVGFEComponentTransferElement>;
    feTable: React.DetailedHTMLProps<React.SVGAttributes<SVGFETableElement>, SVGFETableElement>;
    feTr: React.DetailedHTMLProps<React.SVGAttributes<SVGFETrElement>, SVGFETrElement>;
    feTd: React.DetailedHTMLProps<React.SVGAttributes<SVGFETdElement>, SVGFETdElement>;
    feMorphology: React.DetailedHTMLProps<React.SVGAttributes<SVGFEMorphologyElement>, SVGFEMorphologyElement>;
    feConvolveMatrix: React.DetailedHTMLProps<React.SVGAttributes<SVGFEConvolveMatrixElement>, SVGFEConvolveMatrixElement>;
    feDisplacementMap: React.DetailedHTMLProps<React.SVGAttributes<SVGFEDisplacementMapElement>, SVGFEDisplacementMapElement>;
    feTurbulence: React.DetailedHTMLProps<React.SVGAttributes<SVGFETurbulenceElement>, SVGFETurbulenceElement>;
    feSpecularLighting: React.DetailedHTMLProps<React.SVGAttributes<SVGFESpecularLightingElement>, SVGFESpecularLightingElement>;
    feDiffuseLighting: React.DetailedHTMLProps<React.SVGAttributes<SVGFEDiffuseLightingElement>, SVGFEDiffuseLightingElement>;
    fePointLight: React.DetailedHTMLProps<React.SVGAttributes<SVGFEPointLightElement>, SVGFEPointLightElement>;
    feSpotLight: React.DetailedHTMLProps<React.SVGAttributes<SVGFESpotLightElement>, SVGFESpotLightElement>;
    feDistantLight: React.DetailedHTMLProps<React.SVGAttributes<SVGFEDistantLightElement>, SVGFEDistantLightElement>;
    feDropShadow: React.DetailedHTMLProps<React.SVGAttributes<SVGFEDropShadowElement>, SVGFEDropShadowElement>;
    feImage: React.DetailedHTMLProps<React.SVGAttributes<SVGFEImageElement>, SVGFEImageElement>;
    feTile: React.DetailedHTMLProps<React.SVGAttributes<SVGFETileElement>, SVGFETileElement>;
    feFuncR: React.DetailedHTMLProps<React.SVGAttributes<SVGFEFuncRElement>, SVGFEFuncRElement>;
    feFuncG: React.DetailedHTMLProps<React.SVGAttributes<SVGFEFuncGElement>, SVGFEFuncGElement>;
    feFuncB: React.DetailedHTMLProps<React.SVGAttributes<SVGFEFuncBElement>, SVGFEFuncBElement>;
    feFuncA: React.DetailedHTMLProps<React.SVGAttributes<SVGFEFuncAElement>, SVGFEFuncAElement>;
    feComponentTransfer: React.DetailedHTMLProps<React.SVGAttributes<SVGFEComponentTransferElement>, SVGFEComponentTransferElement>;
    feTable: React.DetailedHTMLProps<React.SVGAttributes<SVGFETableElement>, SVGFETableElement>;
    feTr: React.DetailedHTMLProps<React.SVGAttributes<SVGFETrElement>, SVGFETrElement>;
    feTd: React.DetailedHTMLProps<React.SVGAttributes<SVGFETdElement>, SVGFETdElement>;
  }
} 