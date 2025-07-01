# =====================================
# WEBSITE_GENERATOR.PY - ACTUAL WEBSITE FILE GENERATION
# =====================================
# This creates the actual HTML/CSS/JS files from AI-generated content

import os
import json
import logging
import zipfile
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class WebsiteFileGenerator:
    """Generates actual website files from AI agent content"""
    
    def __init__(self):
        self.output_dir = "/tmp/generated_websites"
        self.templates_dir = Path(__file__).parent / "templates"
        
    def generate_complete_website(self, agent_results: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        """Generate complete website files from agent results"""
        
        try:
            # Create unique project directory
            project_name = f"{config['business_type'].replace(' ', '_').lower()}_{config['location'].replace(' ', '_').lower()}"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_dir = f"{self.output_dir}/{project_name}_{timestamp}"
            
            os.makedirs(project_dir, exist_ok=True)
            os.makedirs(f"{project_dir}/css", exist_ok=True)
            os.makedirs(f"{project_dir}/js", exist_ok=True)
            os.makedirs(f"{project_dir}/images", exist_ok=True)
            
            # Extract content from agent results
            market_data = agent_results.get('market_scanner', {})
            content_data = agent_results.get('content_generator', {})
            design_data = agent_results.get('design_system', {})
            
            # Generate HTML files
            files_created = []
            
            # Homepage
            if content_data.get('content_sections', {}).get('homepage'):
                homepage_html = self._generate_homepage_html(
                    content_data['content_sections']['homepage'],
                    design_data,
                    config
                )
                with open(f"{project_dir}/index.html", 'w', encoding='utf-8') as f:
                    f.write(homepage_html)
                files_created.append('index.html')
            
            # About page
            if content_data.get('content_sections', {}).get('about'):
                about_html = self._generate_about_html(
                    content_data['content_sections']['about'],
                    design_data,
                    config
                )
                with open(f"{project_dir}/about.html", 'w', encoding='utf-8') as f:
                    f.write(about_html)
                files_created.append('about.html')
            
            # Services page
            if content_data.get('content_sections', {}).get('services'):
                services_html = self._generate_services_html(
                    content_data['content_sections']['services'],
                    design_data,
                    config
                )
                with open(f"{project_dir}/services.html", 'w', encoding='utf-8') as f:
                    f.write(services_html)
                files_created.append('services.html')
            
            # Contact page
            if content_data.get('content_sections', {}).get('contact'):
                contact_html = self._generate_contact_html(
                    content_data['content_sections']['contact'],
                    design_data,
                    config
                )
                with open(f"{project_dir}/contact.html", 'w', encoding='utf-8') as f:
                    f.write(contact_html)
                files_created.append('contact.html')
            
            # Generate CSS
            css_content = self._generate_css(design_data, config)
            with open(f"{project_dir}/css/main.css", 'w', encoding='utf-8') as f:
                f.write(css_content)
            files_created.append('css/main.css')
            
            # Generate JavaScript
            js_content = self._generate_javascript(config)
            with open(f"{project_dir}/js/main.js", 'w', encoding='utf-8') as f:
                f.write(js_content)
            files_created.append('js/main.js')
            
            # Create ZIP file
            zip_path = f"{project_dir}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_dir)
                        zipf.write(file_path, arcname)
            
            logger.info(f"Website generated successfully: {project_dir}")
            
            return {
                'success': True,
                'project_dir': project_dir,
                'zip_path': zip_path,
                'files_created': files_created,
                'project_name': project_name,
                'timestamp': timestamp
            }
            
        except Exception as e:
            logger.error(f"Website generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_homepage_html(self, content: Dict, design: Dict, config: Dict) -> str:
        """Generate homepage HTML"""
        
        # Extract content data
        if isinstance(content, dict):
            hero_headline = content.get('hero_headline', f'Professional {config["business_type"]} in {config["location"]}')
            hero_subheadline = content.get('hero_subheadline', 'Quality service you can trust')
            value_proposition = content.get('value_proposition', 'We provide exceptional service to our community.')
            services_list = content.get('services_list', [])
            contact_section_text = content.get('contact_section_text', 'Contact us today for a free consultation.')
        else:
            # Fallback if content is raw text
            hero_headline = f'Professional {config["business_type"]} in {config["location"]}'
            hero_subheadline = 'Quality service you can trust'
            value_proposition = str(content)[:200] + '...' if len(str(content)) > 200 else str(content)
            services_list = []
            contact_section_text = 'Contact us today for a free consultation.'
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{hero_headline} | {config['business_type']} {config['location']}</title>
    <meta name="description" content="{value_proposition[:160]}">
    <link rel="stylesheet" href="css/main.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="container">
            <div class="nav-brand">
                <h1>{config['business_type']}</h1>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="about.html">About</a></li>
                <li><a href="services.html">Services</a></li>
                <li><a href="contact.html">Contact</a></li>
            </ul>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <div class="hero-content">
                <h1 class="hero-headline">{hero_headline}</h1>
                <p class="hero-subheadline">{hero_subheadline}</p>
                <div class="hero-buttons">
                    <a href="contact.html" class="btn btn-primary">Get Free Quote</a>
                    <a href="tel:555-123-4567" class="btn btn-secondary">Call Now</a>
                </div>
            </div>
        </div>
    </section>

    <!-- Value Proposition -->
    <section class="value-prop">
        <div class="container">
            <h2>Why Choose Us</h2>
            <p>{value_proposition}</p>
        </div>
    </section>

    <!-- Services Section -->
    <section class="services">
        <div class="container">
            <h2>Our Services</h2>
            <div class="services-grid">"""
        
        # Add services if available
        if services_list:
            for service in services_list[:3]:  # Limit to 3 services
                service_name = service.get('name', 'Service') if isinstance(service, dict) else str(service)
                service_desc = service.get('description', 'Quality service') if isinstance(service, dict) else 'Quality service'
                html += f"""
                <div class="service-card">
                    <h3>{service_name}</h3>
                    <p>{service_desc}</p>
                    <a href="services.html" class="service-link">Learn More</a>
                </div>"""
        else:
            # Default services
            html += f"""
                <div class="service-card">
                    <h3>Quality {config['business_type']}</h3>
                    <p>Professional service with attention to detail.</p>
                    <a href="services.html" class="service-link">Learn More</a>
                </div>
                <div class="service-card">
                    <h3>Emergency Service</h3>
                    <p>Available when you need us most.</p>
                    <a href="contact.html" class="service-link">Contact Us</a>
                </div>
                <div class="service-card">
                    <h3>Local Expertise</h3>
                    <p>Serving {config['location']} with pride.</p>
                    <a href="about.html" class="service-link">About Us</a>
                </div>"""
        
        html += f"""
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section class="contact-cta">
        <div class="container">
            <h2>Ready to Get Started?</h2>
            <p>{contact_section_text}</p>
            <a href="contact.html" class="btn btn-primary">Contact Us Today</a>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>{config['business_type']}</h3>
                    <p>Serving {config['location']} with quality and integrity.</p>
                </div>
                <div class="footer-section">
                    <h4>Contact Info</h4>
                    <p><i class="fas fa-phone"></i> (555) 123-4567</p>
                    <p><i class="fas fa-envelope"></i> info@example.com</p>
                    <p><i class="fas fa-map-marker-alt"></i> {config['location']}</p>
                </div>
                <div class="footer-section">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="about.html">About</a></li>
                        <li><a href="services.html">Services</a></li>
                        <li><a href="contact.html">Contact</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; {datetime.now().year} {config['business_type']}. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="js/main.js"></script>
</body>
</html>"""
        
        return html
    
    def _generate_about_html(self, content: Dict, design: Dict, config: Dict) -> str:
        """Generate about page HTML"""
        
        if isinstance(content, dict):
            page_title = content.get('page_title', f'About {config["business_type"]}')
            company_story = content.get('company_story', 'We are a trusted local business.')
            mission = content.get('mission_statement', 'Our mission is to provide excellent service.')
        else:
            page_title = f'About {config["business_type"]}'
            company_story = str(content)
            mission = 'Our mission is to provide excellent service.'
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} | {config['business_type']} {config['location']}</title>
    <link rel="stylesheet" href="css/main.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <div class="nav-brand">
                <h1>{config['business_type']}</h1>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="about.html" class="active">About</a></li>
                <li><a href="services.html">Services</a></li>
                <li><a href="contact.html">Contact</a></li>
            </ul>
        </div>
    </nav>

    <main class="page-content">
        <div class="container">
            <h1>{page_title}</h1>
            
            <section class="about-story">
                <h2>Our Story</h2>
                <p>{company_story}</p>
            </section>
            
            <section class="mission">
                <h2>Our Mission</h2>
                <p>{mission}</p>
            </section>
            
            <section class="contact-cta">
                <h2>Ready to Work With Us?</h2>
                <a href="contact.html" class="btn btn-primary">Get In Touch</a>
            </section>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; {datetime.now().year} {config['business_type']}. All rights reserved.</p>
        </div>
    </footer>

    <script src="js/main.js"></script>
</body>
</html>"""
    
    def _generate_services_html(self, content: Dict, design: Dict, config: Dict) -> str:
        """Generate services page HTML"""
        
        services_html = ""
        if isinstance(content, dict) and 'main_services' in content:
            for service in content['main_services']:
                services_html += f"""
                <div class="service-detail">
                    <h3>{service.get('name', 'Service')}</h3>
                    <p>{service.get('description', 'Quality service description.')}</p>
                </div>"""
        else:
            services_html = f"<p>{str(content)}</p>"
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Services | {config['business_type']} {config['location']}</title>
    <link rel="stylesheet" href="css/main.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <div class="nav-brand">
                <h1>{config['business_type']}</h1>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="about.html">About</a></li>
                <li><a href="services.html" class="active">Services</a></li>
                <li><a href="contact.html">Contact</a></li>
            </ul>
        </div>
    </nav>

    <main class="page-content">
        <div class="container">
            <h1>Our Services</h1>
            <div class="services-content">
                {services_html}
            </div>
            
            <section class="contact-cta">
                <h2>Need Our Services?</h2>
                <a href="contact.html" class="btn btn-primary">Request Quote</a>
            </section>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; {datetime.now().year} {config['business_type']}. All rights reserved.</p>
        </div>
    </footer>

    <script src="js/main.js"></script>
</body>
</html>"""
    
    def _generate_contact_html(self, content: Dict, design: Dict, config: Dict) -> str:
        """Generate contact page HTML"""
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact | {config['business_type']} {config['location']}</title>
    <link rel="stylesheet" href="css/main.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <div class="nav-brand">
                <h1>{config['business_type']}</h1>
            </div>
            <ul class="nav-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="about.html">About</a></li>
                <li><a href="services.html">Services</a></li>
                <li><a href="contact.html" class="active">Contact</a></li>
            </ul>
        </div>
    </nav>

    <main class="page-content">
        <div class="container">
            <h1>Contact Us</h1>
            
            <div class="contact-info">
                <div class="contact-method">
                    <h3>Phone</h3>
                    <p>(555) 123-4567</p>
                </div>
                <div class="contact-method">
                    <h3>Email</h3>
                    <p>info@example.com</p>
                </div>
                <div class="contact-method">
                    <h3>Location</h3>
                    <p>{config['location']}</p>
                </div>
            </div>
            
            <form class="contact-form">
                <div class="form-group">
                    <label for="name">Name</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="phone">Phone</label>
                    <input type="tel" id="phone" name="phone">
                </div>
                <div class="form-group">
                    <label for="message">Message</label>
                    <textarea id="message" name="message" rows="5" required></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Send Message</button>
            </form>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; {datetime.now().year} {config['business_type']}. All rights reserved.</p>
        </div>
    </footer>

    <script src="js/main.js"></script>
</body>
</html>"""
    
    def _generate_css(self, design: Dict, config: Dict) -> str:
        """Generate main CSS file"""
        
        return """/* SEO Agent Generated CSS */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Navigation */
.navbar {
    background: #2c3e50;
    color: white;
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 100;
}

.navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-brand h1 {
    font-size: 1.5rem;
}

.nav-menu {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-menu a {
    color: white;
    text-decoration: none;
    transition: color 0.3s;
}

.nav-menu a:hover,
.nav-menu a.active {
    color: #3498db;
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, #3498db, #2c3e50);
    color: white;
    padding: 6rem 0;
    text-align: center;
}

.hero-headline {
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 1rem;
}

.hero-subheadline {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

.hero-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

/* Buttons */
.btn {
    display: inline-block;
    padding: 12px 30px;
    border-radius: 5px;
    text-decoration: none;
    font-weight: bold;
    transition: all 0.3s;
    border: none;
    cursor: pointer;
}

.btn-primary {
    background: #e74c3c;
    color: white;
}

.btn-primary:hover {
    background: #c0392b;
    transform: translateY(-2px);
}

.btn-secondary {
    background: transparent;
    color: white;
    border: 2px solid white;
}

.btn-secondary:hover {
    background: white;
    color: #2c3e50;
}

/* Sections */
.value-prop,
.services,
.contact-cta {
    padding: 4rem 0;
}

.value-prop {
    background: #f8f9fa;
    text-align: center;
}

.value-prop h2 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: #2c3e50;
}

/* Services Grid */
.services-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.service-card {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform 0.3s;
}

.service-card:hover {
    transform: translateY(-5px);
}

.service-card h3 {
    color: #2c3e50;
    margin-bottom: 1rem;
}

.service-link {
    color: #3498db;
    text-decoration: none;
    font-weight: bold;
}

/* Contact CTA */
.contact-cta {
    background: #2c3e50;
    color: white;
    text-align: center;
}

.contact-cta h2 {
    margin-bottom: 1rem;
}

/* Page Content */
.page-content {
    padding: 4rem 0;
    min-height: 60vh;
}

.page-content h1 {
    font-size: 2.5rem;
    margin-bottom: 2rem;
    color: #2c3e50;
}

/* Contact Form */
.contact-form {
    max-width: 600px;
    margin: 2rem auto;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1rem;
}

.contact-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
}

.contact-method {
    text-align: center;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 10px;
}

/* Footer */
.footer {
    background: #2c3e50;
    color: white;
    padding: 3rem 0 1rem;
}

.footer-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}

.footer-section h3,
.footer-section h4 {
    margin-bottom: 1rem;
}

.footer-section ul {
    list-style: none;
}

.footer-section ul li {
    margin-bottom: 0.5rem;
}

.footer-section a {
    color: #bdc3c7;
    text-decoration: none;
}

.footer-section a:hover {
    color: white;
}

.footer-bottom {
    border-top: 1px solid #34495e;
    padding-top: 1rem;
    text-align: center;
    color: #bdc3c7;
}

/* Responsive Design */
@media (max-width: 768px) {
    .hero-headline {
        font-size: 2rem;
    }
    
    .hero-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .nav-menu {
        flex-direction: column;
        gap: 1rem;
    }
    
    .navbar .container {
        flex-direction: column;
        gap: 1rem;
    }
}"""
    
    def _generate_javascript(self, config: Dict) -> str:
        """Generate main JavaScript file"""
        
        return """// SEO Agent Generated JavaScript

// Contact form handling
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.querySelector('.contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(contactForm);
            const data = Object.fromEntries(formData);
            
            // Simple validation
            if (!data.name || !data.email || !data.message) {
                alert('Please fill in all required fields.');
                return;
            }
            
            // Show success message (in real implementation, you'd send to server)
            alert('Thank you for your message! We will get back to you soon.');
            contactForm.reset();
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Mobile menu toggle (if needed)
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
});

// Add some interactive effects
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
    } else {
        navbar.style.boxShadow = 'none';
    }
});"""