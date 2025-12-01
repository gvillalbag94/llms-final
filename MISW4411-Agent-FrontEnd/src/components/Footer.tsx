/**
 * @fileoverview Footer Component
 * 
 * Pie de página de la aplicación con información institucional y enlaces sociales.
 * Incluye logos de la universidad, enlaces a redes sociales y información de copyright.
 * Utiliza animaciones de Framer Motion para efectos visuales atractivos.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

import React from 'react';
import { motion } from 'framer-motion';
import { 
  Facebook,
  Instagram,
  Linkedin,
  Twitter,
  Youtube,
  Copyright
} from 'lucide-react';
import { RiTiktokFill } from 'react-icons/ri';

/**
 * Pie de página de la aplicación
 * 
 * Funcionalidades principales:
 * - Información institucional de la Universidad de los Andes
 * - Enlaces a redes sociales con iconos animados
 * - Logos institucionales y de la facultad
 * - Información de copyright dinámica
 * - Diseño responsivo y atractivo
 * - Animaciones de entrada escalonadas
 * - Efectos hover en elementos interactivos
 * 
 * @returns JSX.Element
 */
const Footer: React.FC = () => {
  const footerVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const socialLinks = [
    { name: 'Facebook', icon: Facebook, href: 'http://www.facebook.com/DISCUniandes' },
    { name: 'Instagram', icon: Instagram, href: 'https://www.instagram.com/discuniandes/' },
    { name: 'LinkedIn', icon: Linkedin, href: 'https://www.linkedin.com/company/departamento-de-ingenier%C3%ADa-de-sistemas-y-computaci%C3%B3n?trk=company_name' },
    { name: 'TikTok', icon: RiTiktokFill, href: 'https://www.tiktok.com/@discuniandes?_t=8Zk7Dhqx9XR&_r=1' },
    { name: 'Twitter', icon: Twitter, href: 'http://twitter.com/DISCUniandes' },
    { name: 'YouTube', icon: Youtube, href: 'https://www.youtube.com/channel/UCpaPKOypMk3xyriPVxkaYkg/videos' },
  ];

  const quickLinks = [
    { name: 'Apoyo Financiero', href: 'https://apoyofinanciero.uniandes.edu.co/' },
    { name: 'Admisiones y Registro', href: 'http://registro.uniandes.edu.co/' },
    { name: 'Biblioteca', href: 'http://biblioteca.uniandes.edu.co/' },
    { name: 'Bloque Neón', href: 'https://bloqueneon.uniandes.edu.co/' },
    { name: 'Agenda y Eventos', href: 'http://eventos.uniandes.edu.co/' },
    { name: 'Decanatura de Estudiantes', href: 'http://decanaturadeestudiantes.uniandes.edu.co/' },
    { name: 'MAAD', href: 'https://uniandes.edu.co/maad' },
  ];

  return (
    <footer 
      className="relative overflow-hidden transition-all duration-300"
      style={{ 
        background: '#342276',
        color: 'white'
      }}
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(52,34,118,0.3),transparent_50%)]"></div>
      </div>

      <div className="relative z-10">
        {/* Main Footer Content */}
        <div className="container mx-auto px-4 py-12">
          <motion.div
            variants={footerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            className="text-center space-y-8"
          >
            {/* Redes Sociales */}
            <motion.div variants={itemVariants}>
              <div className="flex justify-center space-x-4 mb-8">
                {socialLinks.map((social) => {
                  const IconComponent = social.icon;
                  return (
                    <motion.a
                      key={social.name}
                      href={social.href}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className="w-12 h-12 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-all duration-300"
                    >
                      <IconComponent className="w-6 h-6 text-white" />
                    </motion.a>
                  );
                })}
              </div>
            </motion.div>

            {/* Enlaces Rápidos */}
            <motion.div variants={itemVariants}>
              <div className="flex flex-wrap justify-center items-center gap-x-1 gap-y-2 mb-8">
                {quickLinks.map((link, index) => (
                  <React.Fragment key={link.name}>
                    <a
                      href={link.href}
                      className="text-white/90 hover:text-white transition-colors duration-300 text-sm"
                    >
                      {link.name}
                    </a>
                    {index < quickLinks.length - 1 && (
                      <span className="text-white/60 text-sm">|</span>
                    )}
                  </React.Fragment>
                ))}
              </div>
            </motion.div>

            {/* Información Legal */}
            <motion.div variants={itemVariants} className="space-y-3 text-white/80 text-sm">
              <p>Universidad de los Andes | Vigilada Mineducación</p>
              <p>Reconocimiento como Universidad: Decreto 1297 del 30 de mayo de 1964.</p>
              <p>Reconocimiento personería jurídica: Resolución 28 del 23 de febrero de 1949 Minjusticia</p>
              <p>Edificio Mario Laserna Cra 1Este No 19a - 40 Bogotá (Colombia) | Tel: +57 601 3394949 Ext: 2860, 2861, 2862 | Fax +57 601 3324325</p>
            </motion.div>

            {/* Copyright */}
            <motion.div variants={itemVariants} className="pt-4 border-t border-white/20">
              <div className="flex items-center justify-center space-x-2 text-white/70 text-sm">
                <Copyright className="w-4 h-4" />
                <span>2025 - Departamento de Ingeniería de Sistemas y Computación</span>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;