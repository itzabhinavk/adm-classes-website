<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Polytechnic Courses - ADM Classes</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
  <link rel="stylesheet" href="../../../assets/css/style.css" />
  
</head>
<body>
      <div class="blur-bg" id="blurBg"></div>

      <header>
        <div class="logo-section">
      <div class="logo-left">
        <a href="../index/index.php"><img src="../../../assets/images/logo.png" alt="ADM Logo" /></a>
        <div class="logo-text">ADM Classes</div>
      </div>
      <div class="auth-buttons">
        <a href="#" onclick="openModal('login')">Login</a>
        <a href="#" onclick="openModal('register')">Register</a>
        <button class="toggle-btn" onclick="toggleMode()">🌙</button>
      </div>
      <button class="menu-toggle" onclick="toggleMenu()">☰</button>
        </div>
  </header> 

  <nav>
    <div class="nav-links" id="navLinks">
      <a href="../index/index.php" >Home</a>
      <a href="courses.php" class="active">Courses</a>
      <a href="../notes/notes.php">Notes</a>
      <a href="../videos/videos.php">Videos</a>
      <a href="../quiz/quiz.php">Quiz</a>
      <a href="../contact/contact.php">Contact</a>
      <a href="../about/about.php">About</a>
    </div>
  </nav>

  <section class="courses-container">
    <h1>Choose Your Semester</h1>
    <div class="course-grid">
      <div class="course-card">
        <img src="../../../assets/images/logo.png" alt="Branch Logo">
        <h3>1st Semester</h3>
        <a href="semester.php">View Courses</a>
        <h6>available</h6>

      </div>
      <div class="course-card">
        <img src="../../../assets/images/logo.png" alt="Branch Logo">
        <h3>2nd Semester</h3>
        <a href="semester.php">View Courses</a>
      </div>
      <div class="course-card">
        <img src="../../../assets/images/logo.png" alt="Branch Logo">
        <h3>3rd Semester</h3>
        
        <a href="semester.php">View Courses</a>
        <h6>available</h6>
      </div>
      <div class="course-card">
        <img src="../../../assets/images/logo.png" alt="Branch Logo">
        <h3>4th Semester</h3>
        <a href="semester.php">View Courses</a>
      </div>
      <div class="course-card">
        <img src="../../../assets/images/logo.png" alt="Branch Logo">
        <h3>5th Semester</h3>
        
        <a href="semester.php">View Courses</a>
        <h6>available</h6>
      </div>
      <div class="course-card">
        <img src="../../../assets/images/logo.png" alt="Branch Logo">
        <h3>6th Semester</h3>
        <a href="semester.php">View Courses</a>

      </div>
    </div>
  </section>
    <!-- Login Modal -->
  <div class="modal" id="loginModal">
    <span class="close-btn" onclick="closeModal()">&times;</span>
    <h2>Login</h2>
    <input type="email" placeholder="Email" />
    <input type="password" placeholder="Password" />
    <a href="#" onclick="alert('Login successful!');"><button>Login</button></a>
    <div class="switch">Not registered? <a href="#" onclick="switchModal('register')">Register here</a></div>
  </div>

  <!-- Register Modal -->
  <div class="modal" id="registerModal">
    <span class="close-btn" onclick="closeModal()">&times;</span>
    <h2>Register</h2>
    <input type="text" placeholder="Full Name" />
    <input type="email" placeholder="Email" />
    <input type="tel" placeholder="Mobile Number" />
    <input type="password" placeholder="Password" />
    <a href="#" onclick="alert('Registration successful!');"><button>Register</button></a>
    <div class="switch">Already registered? <a href="#" onclick="switchModal('login')">Login here</a></div>
  </div>

  <footer>
    <div>
      <h4>About ADM</h4>
      <ul>
        <li><a href="about.php">Our Mission</a></li>
        <li><a href="#">Team</a></li>
        <li><a href="#">Careers</a></li>
      </ul>
    </div>
    <div>
      <h4>Resources</h4>
      <ul>
        <li><a href="courses.php">Courses</a></li>
        <li><a href="notes.php">Notes</a></li>
        <li><a href="videos.php">Videos</a></li>
      </ul>
    </div>
    <div>
      <h4>Support</h4>
      <ul>
        <li><a href="contact.php">Contact</a></li>
        <li><a href="#">FAQ</a></li>
        <li><a href="#">Privacy Policy</a></li>
      </ul>
    </div>
    <div class="footer-bottom">
      &copy; 2025 ADM Classes | Designed with ❤️ by Abhinav
    </div>
  </footer>

<script src=\"../../../assets/js/script.js\"></script>
</body>
</html>
