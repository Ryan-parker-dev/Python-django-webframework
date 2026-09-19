import random
import time
from flask import Flask, request, session, jsonify

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-me"

# ---------------------------------------------------------------------------
# In-memory OTP store: { email: {"code": "123456", "expires": <timestamp>} }
# This is a DEMO verification flow. In production the code would be sent to
# the applicant's own inbox via a real provider (e.g. Twilio, SendGrid, SES).
# Because this script has no outbound network/email access, the "send" step
# just logs to the server console, clearly labeled as a dev-mode stand-in.
# Nothing about a visitor's device, browser, or physical location is ever
# collected here -- the only thing captured is the country they deliberately
# choose from the dropdown, exactly like any normal address field.
# ---------------------------------------------------------------------------
otp_store = {}
OTP_TTL_SECONDS = 300  # 5 minutes

COUNTRIES = [
    "United States", "Canada", "United Kingdom", "Ireland", "Germany", "France",
    "Netherlands", "Belgium", "Switzerland", "Austria", "Italy", "Spain",
    "Portugal", "Sweden", "Norway", "Denmark", "Finland", "Poland", "Greece",
    "India", "Pakistan", "Bangladesh", "Sri Lanka", "Nepal", "China", "Japan",
    "South Korea", "Singapore", "Malaysia", "Indonesia", "Philippines",
    "Vietnam", "Thailand", "Australia", "New Zealand", "United Arab Emirates",
    "Saudi Arabia", "Qatar", "Israel", "Turkey", "Egypt", "South Africa",
    "Nigeria", "Kenya", "Ghana", "Brazil", "Mexico", "Argentina", "Chile",
    "Colombia", "Peru", "Other",
]

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nova Global University</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#1c1712;
    --maroon:#6d1a2b;
    --maroon-deep:#4a1220;
    --brass:#b28a4a;
    --brass-light:#dcc79a;
    --parchment:#f6f2e9;
    --paper-dark:#171310;
    --slate:#6b6459;
    --line:rgba(178,138,74,.35);
    --good:#3f7d51;
    --bad:#a3372f;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{background:var(--parchment);color:var(--ink);font-family:'Inter',sans-serif;line-height:1.6}
  h1,h2,h3{font-family:'Fraunces',serif;font-weight:500;letter-spacing:-.01em}
  a{color:inherit}
  img{max-width:100%;display:block}
  .eyebrow{
    font-family:'IBM Plex Mono',monospace;
    font-size:12px;letter-spacing:.14em;text-transform:uppercase;
    color:var(--brass);display:flex;align-items:center;gap:10px;margin-bottom:14px;
  }
  .eyebrow::before{content:"";width:26px;height:1px;background:var(--brass)}
  .eyebrow.light{color:var(--brass-light)}
  .eyebrow.light::before{background:var(--brass-light)}

  /* NAV */
  nav{
    position:fixed;top:0;left:0;width:100%;z-index:1000;
    display:flex;align-items:center;justify-content:space-between;
    padding:20px 6%;background:rgba(23,19,16,.92);backdrop-filter:blur(6px);
    border-bottom:1px solid var(--line);
  }
  .brand{display:flex;align-items:center;gap:10px;color:var(--parchment)}
  .brand-mark{width:30px;height:30px;border:1.5px solid var(--brass);border-radius:50%;
    display:flex;align-items:center;justify-content:center;font-family:'Fraunces',serif;
    font-size:14px;color:var(--brass-light)}
  .brand-name{font-family:'Fraunces',serif;font-size:19px;letter-spacing:.01em}
  .nav-links{display:flex;gap:34px}
  .nav-links a{font-size:14px;color:#e8dfd0;text-decoration:none;letter-spacing:.02em}
  .nav-links a:hover{color:var(--brass-light)}

  /* HERO */
  .hero{
    min-height:100vh;background:var(--paper-dark);color:var(--parchment);
    display:grid;grid-template-columns:1.3fr 1fr;align-items:center;gap:40px;
    padding:140px 6% 80px;position:relative;overflow:hidden;
  }
  .hero::after{
    content:"";position:absolute;right:-6%;top:0;bottom:0;width:55%;
    background-image:url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600"><g fill="none" stroke="%23b28a4a" stroke-width="1" opacity="0.35"><path d="M40 560 V220 M100 560 V220 M160 560 V220 M220 560 V220 M280 560 V220 M340 560 V220"/><path d="M20 220 L200 60 L380 220 Z"/><path d="M20 560 H380"/><path d="M10 220 H390"/></g></svg>');
    background-repeat:no-repeat;background-position:center;background-size:contain;
    opacity:.7;pointer-events:none;
  }
  .hero-copy{position:relative;z-index:2}
  .hero h1{font-size:clamp(38px,4.4vw,64px);line-height:1.08;max-width:12ch}
  .hero p{margin:22px 0 34px;max-width:46ch;color:#d8cfc0;font-size:17px}
  .hero-ctas{display:flex;gap:16px;flex-wrap:wrap}
  .btn{
    display:inline-block;padding:15px 28px;border-radius:2px;font-size:14px;
    letter-spacing:.03em;text-decoration:none;font-weight:600;transition:.2s ease;
    border:1px solid transparent;cursor:pointer;
  }
  .btn-primary{background:var(--brass);color:var(--paper-dark);box-shadow:0 8px 20px -8px rgba(178,138,74,.6)}
  .btn-primary:hover{background:var(--brass-light);transform:translateY(-1px)}
  .btn-ghost{border:1px solid var(--line);color:var(--parchment);background:transparent}
  .btn-ghost:hover{border-color:var(--brass);transform:translateY(-1px)}
  .btn-block{width:100%}
  .btn:disabled{opacity:.5;cursor:not-allowed}

  /* FEATURES BAR */
  .features-bar{
    background:#fff;border-bottom:1px solid var(--line);
    display:grid;grid-template-columns:repeat(4,1fr);
  }
  .feature{
    padding:26px 22px;display:flex;gap:14px;align-items:flex-start;
    border-right:1px solid var(--line);
  }
  .feature:last-child{border-right:none}
  .feature-icon{
    width:38px;height:38px;flex-shrink:0;border-radius:50%;
    background:var(--parchment);border:1px solid var(--line);
    display:flex;align-items:center;justify-content:center;
    color:var(--maroon);font-family:'Fraunces',serif;font-size:16px;
  }
  .feature-body h4{font-size:14px;font-weight:600;margin-bottom:4px;letter-spacing:.01em}
  .feature-body p{font-size:12.5px;color:var(--slate);line-height:1.5}
  @media (max-width:860px){
    .features-bar{grid-template-columns:repeat(2,1fr)}
    .feature{border-bottom:1px solid var(--line)}
  }

  .plaque{
    position:relative;z-index:2;background:rgba(246,242,233,.04);
    border:1px solid var(--line);padding:36px 30px;backdrop-filter:blur(2px);
  }
  .plaque-title{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.14em;
    text-transform:uppercase;color:var(--brass-light);margin-bottom:22px}
  .plaque-row{display:flex;justify-content:space-between;padding:14px 0;
    border-top:1px solid var(--line);font-size:14px}
  .plaque-row:last-child{border-bottom:1px solid var(--line)}
  .plaque-row span:first-child{color:#c9bfae}
  .plaque-row span:last-child{font-family:'Fraunces',serif;font-size:18px;color:var(--parchment)}

  /* SECTIONS */
  section{padding:110px 6%}
  .section-head{max-width:640px;margin-bottom:56px}
  .section-head h2{font-size:clamp(28px,3vw,42px)}
  .section-head p{color:var(--slate);margin-top:14px;font-size:16px;max-width:56ch}

  /* ABOUT */
  #about{display:grid;grid-template-columns:1fr 1fr;gap:70px;align-items:center}
  #about p{color:var(--slate);max-width:52ch;font-size:16px;margin-bottom:16px}
  .about-figure{border:1px solid var(--line);padding:40px;background:#fff}
  .about-figure svg{width:100%;height:auto;display:block}
  .about-stats{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:var(--line);
    border:1px solid var(--line);margin-top:30px}
  .about-stat{background:var(--parchment);padding:22px}
  .about-stat b{display:block;font-family:'Fraunces',serif;font-size:28px;color:var(--maroon)}
  .about-stat span{font-size:13px;color:var(--slate)}

  /* HISTORY / TIMELINE */
  #history{background:#fff}
  .timeline{border-left:1px solid var(--line);padding-left:30px;display:flex;flex-direction:column;gap:34px;max-width:720px}
  .tl-item .code{font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--brass);letter-spacing:.1em}
  .tl-item h3{font-size:19px;margin:6px 0}
  .tl-item p{color:var(--slate);font-size:15px;max-width:60ch}

  /* CAMPUS IMAGE BAND */
  .image-band{padding:0;display:grid;grid-template-columns:1.6fr 1fr;gap:2px;background:var(--line)}
  .image-band img{width:100%;height:640px;object-fit:cover}
  .image-band .stack{display:grid;grid-template-rows:1fr 1fr;gap:2px}
  .image-band .stack img{height:319px}

  /* SCHOOLS */
  #schools{background:var(--ink);color:var(--parchment)}
  #schools .section-head p{color:#bdb2a0}
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1px;
    background:var(--line);border:1px solid var(--line)}
  .card{background:var(--ink);padding:34px 28px;transition:.2s ease}
  .card:hover{background:#24201a;transform:translateY(-3px)}
  .card img{width:100%;height:170px;object-fit:cover;margin-bottom:20px;filter:grayscale(.2) contrast(1.05)}
  .card .code{font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--brass);
    letter-spacing:.1em;display:block;margin-bottom:16px}
  .card h3{font-size:21px;margin-bottom:10px}
  .card p{color:#a89e8c;font-size:14.5px;margin-bottom:16px}
  .card ul{list-style:none;color:#a89e8c;font-size:13.5px;display:flex;flex-direction:column;gap:6px}
  .card ul li::before{content:"— ";color:var(--brass)}

  /* FACULTY */
  #faculty{background:var(--parchment)}
  .faculty-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:30px}
  .faculty-card{background:#fff;border:1px solid var(--line);transition:.2s ease}
  .faculty-card:hover{transform:translateY(-4px);box-shadow:0 16px 30px -18px rgba(28,23,18,.35)}
  .faculty-card img{width:100%;height:260px;object-fit:cover}
  .faculty-body{padding:20px}
  .faculty-body h3{font-size:17px;margin-bottom:2px}
  .faculty-body .role{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--brass);
    letter-spacing:.06em;text-transform:uppercase;margin-bottom:10px;display:block}
  .faculty-body p{font-size:13.5px;color:var(--slate)}

  /* TESTIMONIALS */
  #voices{background:var(--maroon);color:var(--parchment)}
  #voices .section-head p{color:#e5c9c9}
  .quotes{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:30px}
  .quote{border:1px solid rgba(246,242,233,.25);padding:30px}
  .quote p{font-family:'Fraunces',serif;font-size:19px;margin-bottom:18px;line-height:1.4}
  .quote .who{font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--brass-light);letter-spacing:.06em}

  /* ADMISSION PROCESS */
  #process{background:#fff}
  .steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:24px}
  .step{border-top:2px solid var(--brass);padding-top:16px}
  .step .num{font-family:'IBM Plex Mono',monospace;color:var(--brass);font-size:13px}
  .step h3{font-size:17px;margin:8px 0 6px}
  .step p{color:var(--slate);font-size:14px}

  /* ADMISSION FORM */
  #admission{background:var(--parchment)}
  .form-wrap{max-width:640px;margin:0 auto;background:#fff;border:1px solid var(--line);
    box-shadow:0 20px 50px -25px rgba(0,0,0,.25)}
  .form-top{background:var(--maroon);color:var(--parchment);padding:26px 34px}
  .form-top .eyebrow{color:var(--brass-light);margin-bottom:8px}
  .form-top .eyebrow::before{background:var(--brass-light)}
  .form-top h3{font-size:22px}
  form{padding:34px}
  .field{margin-bottom:20px}
  .field-row{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:end}
  label{display:block;font-family:'IBM Plex Mono',monospace;font-size:11px;
    letter-spacing:.08em;text-transform:uppercase;color:var(--slate);margin-bottom:8px}
  input,select{
    width:100%;padding:13px 14px;border:1px solid #d8cfbd;border-radius:2px;
    font-family:'Inter',sans-serif;font-size:15px;background:var(--parchment);color:var(--ink);
  }
  input:focus,select:focus{outline:2px solid var(--maroon);outline-offset:1px;border-color:var(--maroon)}
  input:disabled{opacity:.6}
  .otp-btn{white-space:nowrap;padding:13px 18px;font-size:13px;background:var(--ink);color:#fff;
    border:0;border-radius:2px;cursor:pointer}
  .otp-btn:hover{background:#000}
  .otp-status{font-size:13px;margin-top:8px;min-height:18px}
  .otp-status.ok{color:var(--good)}
  .otp-status.err{color:var(--bad)}
  .note{font-size:12.5px;color:var(--slate);margin-top:6px}
  button[type="submit"]{
    width:100%;padding:15px;background:var(--maroon);color:#fff;border:0;border-radius:2px;
    font-size:15px;font-weight:600;letter-spacing:.02em;cursor:pointer;transition:.2s ease;
  }
  button[type="submit"]:hover{background:var(--maroon-deep)}
  button[type="submit"]:disabled{background:#b8a99f;cursor:not-allowed}

  footer{background:var(--paper-dark);color:#a89e8c;text-align:center;padding:38px 20px;
    font-size:13px;letter-spacing:.02em;border-top:1px solid var(--line)}

  @media (max-width:860px){
    .hero{grid-template-columns:1fr}
    .hero::after{display:none}
    #about{grid-template-columns:1fr}
    .nav-links{display:none}
    .image-band{grid-template-columns:1fr}
    .image-band img{height:320px}
    .image-band .stack img{height:159px}
  }
</style>
</head>
<body>

<nav>
  <div class="brand">
    <div class="brand-mark">N</div>
    <div class="brand-name">Nova Global University</div>
  </div>
  <div class="nav-links">
    <a href="#about">About</a>
    <a href="#history">History</a>
    <a href="#schools">Schools</a>
    <a href="#faculty">Faculty</a>
    <a href="#admission">Admission</a>
  </div>
</nav>

<div class="hero">
  <div class="hero-copy">
    <div class="eyebrow light">Est. 1988 &mdash; Charter No. 014</div>
    <h1>Shape the mind that shapes the world.</h1>
    <p>Four schools, one standard of rigor. Nova Global trains engineers, physicians,
    scientists and leaders to work at the edge of what's known.</p>
    <div class="hero-ctas">
      <a class="btn btn-primary" href="#admission">Apply Now</a>
      <a class="btn btn-ghost" href="#schools">Explore Schools</a>
    </div>
  </div>
  <div class="plaque">
    <div class="plaque-title">Nova, by the numbers</div>
    <div class="plaque-row"><span>Founded</span><span>1988</span></div>
    <div class="plaque-row"><span>Schools</span><span>04</span></div>
    <div class="plaque-row"><span>Enrolled students</span><span>12,400</span></div>
    <div class="plaque-row"><span>Acceptance rate</span><span>18%</span></div>
  </div>
</div>

<div class="features-bar">
  <div class="feature">
    <div class="feature-icon">&#9998;</div>
    <div class="feature-body">
      <h4>Rolling admissions</h4>
      <p>Apply any time of year, decisions in 4&ndash;6 weeks.</p>
    </div>
  </div>
  <div class="feature">
    <div class="feature-icon">&#9993;</div>
    <div class="feature-body">
      <h4>Verified applications</h4>
      <p>Every submission is confirmed by a one-time email code.</p>
    </div>
  </div>
  <div class="feature">
    <div class="feature-icon">&#127760;</div>
    <div class="feature-body">
      <h4>38 countries</h4>
      <p>Applicants routed to the right regional office automatically.</p>
    </div>
  </div>
  <div class="feature">
    <div class="feature-icon">&#127891;</div>
    <div class="feature-body">
      <h4>96% placement</h4>
      <p>Graduates placed within six months across all four schools.</p>
    </div>
  </div>
</div>

<section id="about">
  <div>
    <div class="eyebrow">About Nova</div>
    <h2>Built on inquiry, not tradition for its own sake.</h2>
    <p>Nova Global University is a fictional university site built with Flask, styled
    to feel like an institution with real history rather than a template. Every
    school runs on the same principle: ask a harder question than the one you were given.</p>
    <p>Nova sits on a 210-acre campus organized around a single library spine, with
    each school's building branching off it &mdash; the idea being that no discipline
    here is more than a five-minute walk from any other.</p>
    <div class="about-stats">
      <div class="about-stat"><b>38</b><span>Countries represented</span></div>
      <div class="about-stat"><b>870</b><span>Faculty members</span></div>
      <div class="about-stat"><b>210</b><span>Acres of campus</span></div>
      <div class="about-stat"><b>96%</b><span>Placement within 6 months</span></div>
    </div>
  </div>
  <div class="about-figure">
    <svg viewBox="0 0 300 220" xmlns="http://www.w3.org/2000/svg">
      <g fill="none" stroke="#6d1a2b" stroke-width="1.4">
        <path d="M20 200 V90 M60 200 V90 M100 200 V90 M150 200 V90 M200 200 V90 M240 200 V90 M280 200 V90"/>
        <path d="M10 90 L150 20 L290 90 Z"/>
        <path d="M10 200 H290"/>
        <path d="M5 90 H295"/>
      </g>
    </svg>
  </div>
</section>

<section id="history">
  <div class="section-head">
    <div class="eyebrow">Since 1988</div>
    <h2>A short institutional history.</h2>
    <p>Nova grew from a single engineering annex into a four-school university
    without ever changing its founding rule: teach from the primary source, not the summary.</p>
  </div>
  <div class="timeline">
    <div class="tl-item">
      <span class="code">1988</span>
      <h3>Founding charter</h3>
      <p>Nova opens with a single school of engineering and 340 students.</p>
    </div>
    <div class="tl-item">
      <span class="code">1996</span>
      <h3>School of Science established</h3>
      <p>Physics, chemistry, and mathematics separate from engineering into their own faculty.</p>
    </div>
    <div class="tl-item">
      <span class="code">2004</span>
      <h3>Teaching hospital opens</h3>
      <p>The School of Medicine admits its first class alongside a 300-bed teaching hospital.</p>
    </div>
    <div class="tl-item">
      <span class="code">2015</span>
      <h3>School of Business founded</h3>
      <p>Management and finance programs launch in partnership with regional industry.</p>
    </div>
    <div class="tl-item">
      <span class="code">2026</span>
      <h3>12,400 students, 38 countries</h3>
      <p>Nova's current enrollment, drawn from secondary schools on six continents.</p>
    </div>
  </div>
</section>

<div class="image-band">
  <img src="https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=1600&q=80" alt="Nova library reading hall">
  <div class="stack">
    <img src="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=900&q=80" alt="Students walking on campus">
    <img src="https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=900&q=80" alt="Lecture hall">
  </div>
</div>

<section id="schools">
  <div class="section-head">
    <div class="eyebrow light">Programs</div>
    <h2>Four schools. One admissions form.</h2>
    <p>Each school shares Nova's core curriculum in the first year, then specializes.</p>
  </div>
  <div class="cards">
    <div class="card">
      <img src="https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80" alt="Engineering lab">
      <span class="code">ENGR &middot; 01</span>
      <h3>Engineering</h3>
      <p>AI systems, robotics, and computer science, taught by people who still build things.</p>
      <ul>
        <li>B.Tech Computer Science &amp; Engineering</li>
        <li>B.Tech Robotics</li>
        <li>M.Eng Applied AI</li>
      </ul>
    </div>
    <div class="card">
      <img src="https://images.unsplash.com/photo-1580281657702-257584239a55?auto=format&fit=crop&w=800&q=80" alt="Medical training">
      <span class="code">MED &middot; 02</span>
      <h3>Medicine</h3>
      <p>Clinical training paired with active research into diagnosis and care.</p>
      <ul>
        <li>MBBS, 6-year track</li>
        <li>BSc Nursing</li>
        <li>MD Internal Medicine</li>
      </ul>
    </div>
    <div class="card">
      <img src="https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=800&q=80" alt="Business students">
      <span class="code">BUS &middot; 03</span>
      <h3>Business</h3>
      <p>Management, finance, and the judgment calls that don't show up in a textbook.</p>
      <ul>
        <li>BBA General Management</li>
        <li>BSc Finance</li>
        <li>MBA, 2-year</li>
      </ul>
    </div>
    <div class="card">
      <img src="https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=800&q=80" alt="Science laboratory">
      <span class="code">SCI &middot; 04</span>
      <h3>Science</h3>
      <p>Physics, chemistry, and mathematics for students who want the proof, not just the result.</p>
      <ul>
        <li>BSc Physics</li>
        <li>BSc Chemistry</li>
        <li>BSc Applied Mathematics</li>
      </ul>
    </div>
  </div>
</section>

<section id="faculty">
  <div class="section-head">
    <div class="eyebrow">Faculty</div>
    <h2>A few of the people teaching here.</h2>
  </div>
  <div class="faculty-grid">
    <div class="faculty-card">
      <img src="https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=500&q=80" alt="Faculty portrait">
      <div class="faculty-body">
        <h3>Dr. Amara Osei</h3>
        <span class="role">Dean, School of Engineering</span>
        <p>Twenty years in applied robotics before joining Nova's founding faculty.</p>
      </div>
    </div>
    <div class="faculty-card">
      <img src="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=500&q=80" alt="Faculty portrait">
      <div class="faculty-body">
        <h3>Dr. Rohan Mehta</h3>
        <span class="role">Dean, School of Medicine</span>
        <p>Leads Nova's teaching hospital and a research group in diagnostic imaging.</p>
      </div>
    </div>
    <div class="faculty-card">
      <img src="https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?auto=format&fit=crop&w=500&q=80" alt="Faculty portrait">
      <div class="faculty-body">
        <h3>Prof. Elena Kovacs</h3>
        <span class="role">Dean, School of Business</span>
        <p>Former operations lead at a logistics firm, now teaching supply-chain strategy.</p>
      </div>
    </div>
    <div class="faculty-card">
      <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=500&q=80" alt="Faculty portrait">
      <div class="faculty-body">
        <h3>Dr. Marcus Lindqvist</h3>
        <span class="role">Dean, School of Science</span>
        <p>Condensed matter physicist, on faculty since Nova's science school opened in 1996.</p>
      </div>
    </div>
  </div>
</section>

<section id="voices">
  <div class="section-head">
    <div class="eyebrow light">Student voices</div>
    <h2>What it's actually like here.</h2>
  </div>
  <div class="quotes">
    <div class="quote">
      <p>"The first-year core curriculum meant I sat next to future doctors and future engineers in the same room."</p>
      <div class="who">Second-year, School of Science</div>
    </div>
    <div class="quote">
      <p>"Office hours here mean the professor asks you a harder question back, not a shortcut."</p>
      <div class="who">Final-year, School of Engineering</div>
    </div>
    <div class="quote">
      <p>"Nova's hospital rotations start earlier than most programs I looked at."</p>
      <div class="who">Third-year, School of Medicine</div>
    </div>
  </div>
</section>

<section id="process">
  <div class="section-head">
    <div class="eyebrow">How admission works</div>
    <h2>Four steps from application to offer.</h2>
  </div>
  <div class="steps">
    <div class="step">
      <span class="num">01</span>
      <h3>Apply online</h3>
      <p>Submit the form below with your details and preferred program.</p>
    </div>
    <div class="step">
      <span class="num">02</span>
      <h3>Verify your email</h3>
      <p>Confirm the one-time code sent to the address you provided.</p>
    </div>
    <div class="step">
      <span class="num">03</span>
      <h3>Document review</h3>
      <p>The registrar's office reviews transcripts and test scores.</p>
    </div>
    <div class="step">
      <span class="num">04</span>
      <h3>Decision</h3>
      <p>Offers are sent by email within four to six weeks.</p>
    </div>
  </div>
</section>

<section id="admission">
  <div class="form-wrap">
    <div class="form-top">
      <div class="eyebrow light">Registrar's Office</div>
      <h3>Online Admission Application</h3>
    </div>
    <form id="admission-form" method="POST" action="/">
      <div class="field">
        <label for="student">Student Name</label>
        <input id="student" name="student" placeholder="Jordan Vance" required>
      </div>

      <div class="field">
        <label for="email">Email</label>
        <div class="field-row">
          <input id="email" name="email" type="email" placeholder="jordan@example.com" required>
          <button type="button" id="send-otp-btn" class="otp-btn">Send code</button>
        </div>
        <div class="note">We'll email a 6-digit code to confirm this address is yours.</div>
      </div>

      <div class="field" id="otp-field" style="display:none">
        <label for="otp">Verification Code</label>
        <div class="field-row">
          <input id="otp" name="otp" inputmode="numeric" maxlength="6" placeholder="000000">
          <button type="button" id="verify-otp-btn" class="otp-btn">Verify</button>
        </div>
        <div class="otp-status" id="otp-status"></div>
      </div>

      <div class="field">
        <label for="phone">Phone Number</label>
        <input id="phone" name="phone" placeholder="(555) 010-2938" required>
      </div>

      <div class="field">
        <label for="country">Country you're applying from</label>
        <select id="country" name="country">
          {country_options}
        </select>
        <div class="note">This is only used to route your application to the right regional office.</div>
      </div>

      <div class="field">
        <label for="course">Program</label>
        <select id="course" name="course">
          <option>B.Tech CSE</option>
          <option>MBBS</option>
          <option>BBA</option>
          <option>BSc Physics</option>
        </select>
      </div>

      <button type="submit" id="submit-btn" disabled>Verify email to submit</button>
    </form>
  </div>
</section>

<footer>&copy; 2026 Nova Global University &mdash; a fictional institution</footer>

<script>
const sendBtn = document.getElementById('send-otp-btn');
const verifyBtn = document.getElementById('verify-otp-btn');
const otpField = document.getElementById('otp-field');
const otpStatus = document.getElementById('otp-status');
const emailInput = document.getElementById('email');
const otpInput = document.getElementById('otp');
const submitBtn = document.getElementById('submit-btn');

sendBtn.addEventListener('click', async () => {
  const email = emailInput.value.trim();
  if (!email) { emailInput.reportValidity(); return; }
  sendBtn.disabled = true;
  sendBtn.textContent = 'Sending...';
  try {
    const res = await fetch('/send-otp', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ email })
    });
    const data = await res.json();
    otpField.style.display = 'block';
    otpStatus.className = 'otp-status ok';
    otpStatus.textContent = data.message;
  } catch (err) {
    otpStatus.className = 'otp-status err';
    otpStatus.textContent = 'Could not send code. Please try again.';
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = 'Resend code';
  }
});

verifyBtn.addEventListener('click', async () => {
  const email = emailInput.value.trim();
  const code = otpInput.value.trim();
  if (!code) { otpInput.reportValidity(); return; }
  verifyBtn.disabled = true;
  try {
    const res = await fetch('/verify-otp', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ email, code })
    });
    const data = await res.json();
    if (data.verified) {
      otpStatus.className = 'otp-status ok';
      otpStatus.textContent = 'Email verified.';
      otpInput.disabled = true;
      verifyBtn.disabled = true;
      sendBtn.disabled = true;
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit Application';
    } else {
      otpStatus.className = 'otp-status err';
      otpStatus.textContent = data.message;
      verifyBtn.disabled = false;
    }
  } catch (err) {
    otpStatus.className = 'otp-status err';
    otpStatus.textContent = 'Verification failed. Please try again.';
    verifyBtn.disabled = false;
  }
});

const navEl = document.querySelector('nav');
window.addEventListener('scroll', () => {
  if (window.scrollY > 40) {
    navEl.style.boxShadow = '0 8px 24px -16px rgba(0,0,0,.6)';
  } else {
    navEl.style.boxShadow = 'none';
  }
});
</script>

</body>
</html>
"""

CONFIRM = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Application Submitted &mdash; Nova Global University</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500&family=Inter:wght@400;500&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{background:#171310;color:#f6f2e9;font-family:'Inter',sans-serif;
    min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:20px}}
  .card{{max-width:480px;border:1px solid rgba(178,138,74,.4);padding:50px 40px}}
  .eyebrow{{font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:.14em;
    text-transform:uppercase;color:#dcc79a;margin-bottom:18px}}
  h1{{font-family:'Fraunces',serif;font-weight:500;font-size:30px;margin-bottom:16px}}
  p{{color:#bdb2a0;margin-bottom:30px;font-size:15px}}
  a{{display:inline-block;padding:13px 26px;background:#b28a4a;color:#171310;
    text-decoration:none;font-weight:600;font-size:14px;border-radius:2px}}
</style>
</head>
<body>
  <div class="card">
    <div class="eyebrow">Registrar's Office</div>
    <h1>Application received.</h1>
    <p>{message}</p>
    <a href="/">Back to home</a>
  </div>
</body>
</html>
"""

REJECT = """
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Verification required</title>
<style>body{{font-family:sans-serif;background:#171310;color:#f6f2e9;display:flex;
align-items:center;justify-content:center;min-height:100vh;text-align:center}}
a{{color:#dcc79a}}</style></head>
<body>
  <div>
    <h1>Please verify your email first.</h1>
    <p><a href="/">Go back and verify your email before submitting.</a></p>
  </div>
</body>
</html>
"""


def render_home():
    options = "\n".join(f'<option>{c}</option>' for c in COUNTRIES)
    return HTML.replace("{country_options}", options)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form.get("email", "")
        if not session.get("otp_verified") or session.get("otp_email") != email:
            return REJECT

        print("=== NEW APPLICATION ===")
        print("Student:", request.form.get("student"))
        print("Email:", email)
        print("Phone:", request.form.get("phone"))
        print("Country:", request.form.get("country"))
        print("Course:", request.form.get("course"))
        print("========================")

        session.pop("otp_verified", None)
        session.pop("otp_email", None)
        otp_store.pop(email, None)

        return CONFIRM.format(
            message="Your application has been logged. Admissions will reach out by email with next steps."
        )
    return render_home()


@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    if not email or "@" not in email:
        return jsonify({"ok": False, "message": "Enter a valid email first."}), 400

    code = f"{random.randint(0, 999999):06d}"
    otp_store[email] = {"code": code, "expires": time.time() + OTP_TTL_SECONDS}

    # DEV MODE ONLY: this script has no email/SMS provider configured, so the
    # code is written to the server console instead of being emailed to the
    # applicant. Wire this up to a real provider (SendGrid, SES, Twilio, etc.)
    # before using this in production -- the applicant should be the only
    # person who ever sees their own code.
    print(f"[DEV OTP] Verification code for {email}: {code} (expires in {OTP_TTL_SECONDS}s)")

    return jsonify({"ok": True, "message": "Code sent. Check the server console for this demo."})


@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    code = data.get("code", "").strip()

    record = otp_store.get(email)
    if not record:
        return jsonify({"verified": False, "message": "Request a code first."})
    if time.time() > record["expires"]:
        otp_store.pop(email, None)
        return jsonify({"verified": False, "message": "Code expired. Send a new one."})
    if code != record["code"]:
        return jsonify({"verified": False, "message": "Incorrect code."})

    session["otp_verified"] = True
    session["otp_email"] = email
    return jsonify({"verified": True, "message": "Email verified."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)