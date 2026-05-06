import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Github, Linkedin, Mail, ArrowUpRight, Sun, Moon, Menu, X, BookOpen, Code2, FileText, Eye } from 'lucide-react';

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeProjectTab, setActiveProjectTab] = useState('All');

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const toggleTheme = () => setDarkMode(!darkMode);

  const projects = [
    { title: "Enterprise Design System", url: "#", category: "Frontend", description: "A comprehensive React component library used by 15+ engineering teams to ensure brand consistency.", skills: ["React", "Storybook", "Tailwind"] },
    { title: "FinTrack API Gateway", url: "#", category: "Backend", description: "High-performance API gateway handling millions of requests daily with Redis caching and rate limiting.", skills: ["Node.js", "Redis", "Docker"] },
    { title: "React-Use-Swipe", url: "#", category: "Open Source", description: "Lightweight, performant React hook for complex swipe interactions on mobile devices. 10k+ weekly downloads.", skills: ["TypeScript", "Jest"] },
    { title: "Corporate Dashboard UI", url: "#", category: "Design", description: "Information-dense dashboard analytics layout designed specifically for the financial sector.", skills: ["Figma", "UI/UX"] }
  ];

  const articles = [
    { date: "May 12, 2024", readTime: "5 min read", views: "1.2k views", title: "Optimizing React Performance in Large Scale Apps", description: "Discover strategies for identifying and fixing performance bottlenecks in large React codebases, utilizing tools like React Profiler and useMemo effectively.", category: "Engineering", url: "#" },
    { date: "Apr 04, 2024", readTime: "8 min read", views: "856 views", title: "Designing for Accessibility: A Practical Guide", description: "Learn how to build inclusive digital experiences with actionable tips on color contrast, keyboard navigation, and ARIA roles for modern web applications.", category: "Design", url: "#" },
    { date: "Jan 28, 2024", readTime: "4 min read", views: "2.3k views", title: "My transition from Frontend to Full Stack", description: "A personal reflection on my journey moving from pure frontend development to embracing backend technologies like Node.js and PostgreSQL.", category: "Career", url: "#" }
  ];

  const projectCategories = ['All', 'Frontend', 'Backend', 'Open Source', 'Design'];
  const filteredProjects = activeProjectTab === 'All' ? projects : projects.filter(p => p.category === activeProjectTab);

  const navLinks = [
    { name: "About", href: "#about" },
    { name: "Experience", href: "#experience" },
    { name: "Projects", href: "#projects" },
    { name: "Articles", href: "#articles" }
  ];

  return (
    <div className="min-h-screen bg-[#FAFAFA] dark:bg-[#09090b] text-slate-800 dark:text-slate-200 transition-colors duration-300 font-sans selection:bg-slate-900 selection:text-white dark:selection:bg-white dark:selection:text-slate-900 relative">
      <div className="absolute inset-0 bg-dot-pattern pointer-events-none [mask-image:radial-gradient(ellipse_at_center,white,transparent_80%)]"></div>
      
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-50 bg-[#FAFAFA]/70 dark:bg-[#09090b]/70 backdrop-blur-md border-b border-slate-200 dark:border-white/10 px-6 py-4">
        <div className="max-w-[1000px] mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-cyan-400 flex items-center justify-center font-bold text-sm text-white shadow-sm">
              L
            </div>
            <span className="font-semibold text-lg tracking-tight">Luna</span>
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-8">
            {navLinks.map(link => (
              <a key={link.name} href={link.href} className="text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                {link.name}
              </a>
            ))}
          </nav>

          <div className="flex items-center gap-4">
            {/* Desktop Socials */}
            <div className="hidden md:flex items-center gap-4 border-r border-slate-200 dark:border-white/10 pr-4 mr-1">
              <a href="#" className="text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"><Github size={18} /></a>
              <a href="#" className="text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"><Linkedin size={18} /></a>
              <a href="#" className="text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"><Mail size={18} /></a>
            </div>

            <button onClick={toggleTheme} className="p-2 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors" title="Toggle Theme">
              {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="md:hidden p-2 -mr-2 text-slate-600 dark:text-slate-300">
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}
            className="md:hidden fixed inset-0 top-[65px] z-40 bg-[#FAFAFA]/95 dark:bg-[#09090b]/95 backdrop-blur-md border-b border-slate-200 dark:border-white/10 p-6 shadow-xl flex flex-col justify-between"
          >
            <nav className="flex flex-col gap-6 mt-4">
              {navLinks.map(link => (
                <a key={link.name} href={link.href} onClick={() => setIsMobileMenuOpen(false)} className="text-lg font-medium text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                  {link.name}
                </a>
              ))}
            </nav>
            <div className="mb-8">
               <a href="/resume.pdf" target="_blank" className="flex items-center justify-center gap-2 w-full py-3 px-4 bg-blue-600 text-white dark:bg-blue-500 rounded-xl font-medium hover:bg-blue-700 dark:hover:bg-blue-600 shadow-md shadow-blue-500/20 transition-all">
                  <FileText size={18} /> View Resume
               </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <main className="max-w-[768px] mx-auto px-6 py-16 md:py-24 relative z-10">
        
        {/* Intro/Hero Section */}
        <section className="mb-24 flex flex-col-reverse md:flex-row gap-10 items-center md:items-start text-center md:text-left">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="flex-1">
            <h1 className="text-4xl lg:text-5xl font-bold tracking-tight mb-4 text-slate-900 dark:text-white">
              Hi, I'm Luna <span className="inline-block animate-wave">👋</span>
            </h1>
            <h2 className="text-xl font-medium text-blue-600 dark:text-blue-400 mb-6">
              Developer & Creator
            </h2>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-base lg:text-lg mb-8">
              I build scalable web applications, robust backend systems, and craft clean, intuitive user interfaces. Passionate about creating accessible and modern digital experiences.
            </p>
            
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-4">
              <a href="#projects" className="inline-flex items-center gap-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 px-6 py-3 rounded-full transition-all shadow-md shadow-blue-500/20">
                 View Projects
              </a>
              <a href="#resume" className="inline-flex items-center gap-2 group text-sm font-medium text-slate-800 dark:text-white bg-white dark:bg-white/5 hover:bg-slate-50 dark:hover:bg-white/10 border border-slate-200 dark:border-white/10 px-6 py-3 rounded-full transition-all shadow-sm">
                 <FileText size={16} className="text-slate-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
                 Resume
              </a>
            </div>
          </motion.div>
          <motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5, delay: 0.1 }}>
            <div className="w-32 h-32 md:w-40 md:h-40 rounded-full bg-gradient-to-tr from-blue-500 to-cyan-400 flex items-center justify-center font-bold text-5xl md:text-6xl text-white shadow-xl shadow-cyan-500/30 shrink-0 ring-4 ring-white dark:ring-[#09090b]">
              L
            </div>
          </motion.div>
        </section>

        {/* About Section */}
        <section id="about" className="mb-28 scroll-mt-20">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3, duration: 0.5 }} className="space-y-6 text-slate-600 dark:text-slate-300 leading-relaxed font-light text-base lg:text-lg">
            <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-6 flex items-center gap-3">
              <span className="w-6 h-[1px] bg-slate-300 dark:bg-white/20 hidden md:block"></span>
              About
            </h3>
            <p>
                Back in 2015, I decided to try my hand at creating custom Tumblr themes and tumbled head first into the rabbit hole of coding and web development. Fast-forward to today, and I've had the privilege of building software for an advertising agency, a start-up, a huge corporation, and a student-led design studio.
              </p>
              <p>
                My main focus these days is building accessible, inclusive products and digital experiences for a variety of clients. I also enjoy writing technical articles and sharing my knowledge with the developer community.
              </p>
              
              <div className="pt-4 flex flex-wrap gap-2 items-center text-sm font-mono text-slate-500 dark:text-slate-400">
                <span className="mr-2 font-sans font-medium text-slate-700 dark:text-slate-300">Stack:</span>
                {['JavaScript/TS', 'React', 'Node.js', 'Next.js', 'PostgreSQL', 'Tailwind CSS'].map(tech => (
                  <span key={tech} className="bg-slate-100 dark:bg-white/5 px-2 py-1 rounded-md">{tech}</span>
                ))}
              </div>
            </motion.div>
          </section>

          <section id="experience" className="mb-28 scroll-mt-20">
            <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-10 flex items-center gap-3">
              <span className="w-6 h-[1px] bg-slate-300 dark:bg-white/20 hidden md:block"></span>
              Experience
            </h3>
            <div className="relative border-l border-slate-200 dark:border-white/10 ml-3 md:ml-4 space-y-12 pb-4">
              <ExperienceItem 
                date="2021 — Present" title="Senior Software Engineer, Core UI" company="TechCorp Inc."
                description="Lead the frontend architecture for the core product dashboard. Mentored a team of 4 engineers and improved performance by 35% through code-splitting and asset optimization."
                skills={['React', 'TypeScript', 'Next.js', 'Tailwind', 'GraphQL']}
              />
              <ExperienceItem 
                date="2018 — 2021" title="Full Stack Developer" company="Growth Startup"
                description="Developed and shipped features for the main consumer-facing application. Engineered a real-time notification system using WebSockets and Redis."
                skills={['React', 'Node.js', 'PostgreSQL', 'Redis', 'AWS']}
              />
            </div>
          </section>

          <section id="projects" className="mb-28 scroll-mt-20">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-10 gap-6">
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white flex items-center gap-3">
                <span className="w-6 h-[1px] bg-slate-300 dark:bg-white/20 hidden md:block"></span>
                Featured Projects
              </h3>
              
              {/* Tab Pagination / Categories */}
              <div className="flex flex-wrap gap-2">
                {projectCategories.map(cat => (
                  <button 
                    key={cat} onClick={() => setActiveProjectTab(cat)}
                    className={`px-3 py-1.5 text-xs font-semibold rounded-full transition-all border ${activeProjectTab === cat ? 'bg-slate-900 text-white border-slate-900 dark:bg-white dark:text-slate-900 dark:border-white shadow-md' : 'bg-transparent text-slate-500 border-slate-200 hover:border-slate-400 dark:text-slate-400 dark:border-white/10 dark:hover:border-white/30'}`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            <motion.div layout className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <AnimatePresence mode="popLayout">
                {filteredProjects.map((project, idx) => (
                  <ProjectCard 
                    key={project.title} 
                    title={project.title}
                    url={project.url}
                    description={project.description}
                    skills={project.skills}
                    category={project.category}
                    featured={idx === 0 && activeProjectTab === 'All'}
                  />
                ))}
              </AnimatePresence>
            </motion.div>
          </section>

          <section id="articles" className="mb-24 scroll-mt-20">
            <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-10 flex items-center gap-3">
              <span className="w-6 h-[1px] bg-slate-300 dark:bg-white/20 hidden md:block"></span>
              Recent Articles
            </h3>
            <div className="flex flex-col gap-6">
              {articles.map(article => (
                <ArticleCard 
                  key={article.title} 
                  date={article.date}
                  readTime={article.readTime}
                  views={article.views}
                  title={article.title}
                  description={article.description}
                  category={article.category}
                  url={article.url}
                />
              ))}
            </div>
            <a href="#" className="inline-flex items-center gap-2 mt-8 text-sm font-semibold text-slate-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors group">
              View all articles 
              <ArrowUpRight size={16} className="transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
            </a>
          </section>

          <footer className="pt-12 border-t border-slate-200 dark:border-white/10 text-sm text-slate-500 dark:text-slate-400 font-light flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <p>
              Built with React & Tailwind CSS. Typography uses Inter and JetBrains Mono.
            </p>
            <p>© {new Date().getFullYear()} Luna. All rights reserved.</p>
          </footer>

        </main>
    </div>
  );
}

// Subcomponents

function ExperienceItem({ title, company, date, description, skills }: { title: string, company: string, date: string, description: string, skills?: string[] }) {
  return (
    <motion.div initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, margin: "-50px" }} transition={{ duration: 0.5 }} className="relative pl-8">
      <div className="absolute w-3 h-3 bg-blue-600 rounded-full -left-[6.5px] top-1.5 ring-4 ring-[#FAFAFA] dark:ring-[#09090b]"></div>
      <div className="flex flex-col sm:flex-row sm:items-baseline gap-1 sm:gap-4 mb-2">
        <h4 className="text-lg font-bold text-slate-900 dark:text-slate-100">{title}</h4>
        <span className="text-sm font-medium text-blue-600 dark:text-blue-400">{company}</span>
      </div>
      <span className="text-xs font-mono text-slate-400 dark:text-slate-500 mb-4 block">{date}</span>
      <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed max-w-2xl mb-4">{description}</p>
      {skills && skills.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {skills.map(skill => (
            <span key={skill} className="text-[11px] font-mono font-semibold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-white/10 px-2.5 py-1 rounded-md">
              {skill}
            </span>
          ))}
        </div>
      )}
    </motion.div>
  );
}

function ProjectCard({ title, url, description, skills, category, featured }: { key?: string, title: string, url: string, description: string, skills: string[], category: string, featured?: boolean }) {
  return (
    <motion.a 
      href={url} target="_blank" rel="noreferrer"
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={`group flex flex-col p-6 border border-slate-200 dark:border-white/10 rounded-2xl hover:border-slate-400 dark:hover:border-white/30 bg-white dark:bg-white/[0.02] hover:bg-white dark:hover:bg-white/[0.04] hover:-translate-y-1 hover:shadow-xl dark:hover:shadow-2xl dark:hover:shadow-black/50 transition-all duration-300 ${featured ? 'md:col-span-2' : ''}`}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-slate-100 dark:bg-white/10 text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white group-hover:bg-slate-200 dark:group-hover:bg-white/20 transition-colors">
            <Code2 size={20} />
          </div>
          <h4 className="text-lg font-semibold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
            {title}
          </h4>
        </div>
        <ArrowUpRight size={20} className="text-slate-400 group-hover:text-slate-900 dark:group-hover:text-white transition-colors -translate-x-1 translate-y-1 group-hover:translate-x-0 group-hover:translate-y-0" />
      </div>
      <p className="text-sm text-slate-600 dark:text-slate-400 mb-6 leading-relaxed">
        {description}
      </p>
      <div className="flex items-center justify-between mt-auto pt-2">
        <div className="flex flex-wrap gap-2 text-wrap">
          {skills.slice(0,3).map(skill => (
             <span key={skill} className="text-[11px] font-mono font-medium text-slate-500 dark:text-slate-400">
               {skill}
             </span>
          ))}
          {skills.length > 3 && <span className="text-[11px] font-mono font-medium text-slate-400">+{skills.length - 3}</span>}
        </div>
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 border border-slate-200 dark:border-white/10 rounded-full px-2.5 py-1">
          {category}
        </span>
      </div>
    </motion.a>
  );
}

function ArticleCard({ date, readTime, views, title, description, category, url }: { key?: string, date: string, readTime: string, views: string, title: string, description: string, category: string, url: string }) {
  return (
    <motion.a 
      href={url} target="_blank" rel="noreferrer" 
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.2 }}
      className="group flex flex-col p-6 border border-slate-200 dark:border-white/10 rounded-2xl hover:border-blue-300 dark:hover:border-blue-500/50 bg-white dark:bg-white/[0.02] hover:bg-white dark:hover:bg-white/[0.04] hover:-translate-y-1 hover:shadow-xl dark:hover:shadow-2xl dark:hover:shadow-black/50 transition-all duration-300 relative overflow-hidden"
    >
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-bold uppercase tracking-wider bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 px-2.5 py-1 rounded-md">
          {category}
        </span>
        <span className="text-xs font-medium text-slate-400 dark:text-slate-500 flex items-center gap-1.5">
          {date}
        </span>
      </div>
      
      <h4 className="text-lg font-bold text-slate-900 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors flex items-center justify-between gap-4 mb-2">
        <span className="line-clamp-2">{title}</span>
        <ArrowUpRight size={20} className="shrink-0 text-slate-300 dark:text-slate-500 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-transform group-hover:-translate-y-1 group-hover:translate-x-1" />
      </h4>

      <p className="text-sm text-slate-600 dark:text-slate-400 mb-6 line-clamp-2 leading-relaxed">
        {description}
      </p>

      <div className="flex items-center gap-4 mt-auto pt-4 border-t border-slate-100 dark:border-white/5 text-xs text-slate-500 dark:text-slate-400 font-medium">
        <span className="flex items-center gap-1.5"><BookOpen size={14} className="text-slate-400" /> {readTime}</span>
        <span className="w-1 h-1 rounded-full bg-slate-300 dark:bg-slate-600"></span>
        <span className="flex items-center gap-1.5"><Eye size={14} className="text-slate-400" /> {views}</span>
      </div>
    </motion.a>
  );
}

