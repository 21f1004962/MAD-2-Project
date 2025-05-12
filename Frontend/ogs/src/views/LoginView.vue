<template>
  <div class="main-content">
    <NavbarVue />
    <div class="center-content">
      <MessagesVue :messages="messages"/>
      <div
        class="container d-flex justify-content-center"
        style="margin-top: 30px"
      >
        <div class="login-box">
          <h2>Login</h2>
          <form @submit.prevent="handleLoginSubmit">
            <label for="username">Username:</label>
            <input
              type="text"
              id="username"
              name="username"
              v-model="username"
              required
            />

            <label for="password">Password:</label>
            <input
              type="password"
              id="password"
              name="password"
              v-model="password"
              required
            />

            <button>Submit</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavbarVue from "../components/Navbar.vue";
import MessagesVue from '../components/Messages.vue';
import axios from "axios";


export default {
  name: "LoginView",
  data(){
    return{
      username: "",
      password: "",
      messages: [],
    }
  },
  components: {
    NavbarVue,
    MessagesVue,
  },
  methods: {
    handleLoginSubmit() {
      const formData = new FormData();
      formData.append("username", this.username);
      formData.append("password", this.password);

      axios
        .post("http://127.0.0.1:5000/login", formData)
        .then((response) => {
          if (response.status === 202) {
            this.showMessage({
              text: "Sign up request still pending. Please try again later!",
              type: 'information',
            });
          } else {
            localStorage.setItem("jwtToken", response.data.token);
            this.username = "";
            this.password = "";
            window.location.reload(true);
          }
        })
        .catch((error) => {
          console.error("Login failed.");
          console.error("Error details:", error);
          this.showMessage({ text: error.response.data, type: 'failure' });
          if (error.response) {
            console.error("Status code:", error.response.status);
            console.error("Response data:", error.response.data);
          } else if (error.request) {
            console.error("No response received:", error.request);
          } else {
            console.error("Error setting up the request:", error.message);
          }
        });
    },
    showMessage(message) {
      this.messages.push(message);

      setTimeout(() => {
        this.messages.shift(); 
      }, 5000);
    },
  },
  beforeCreate() {
    const jwtToken = localStorage.getItem('jwtToken');

    if (!jwtToken) {
      this.$router.push('/login');
    } else {
      try {
        const decodedToken = JSON.parse(atob(jwtToken.split('.')[1]));

        if (Date.now() >= decodedToken.exp * 1000) {
          console.error('Token is expired');
          localStorage.removeItem('jwtToken');
          this.$router.push('/login');
        } else {
          const userRole = decodedToken.role;

          if (userRole === 'admin') {
            this.$router.push('/adminHome');
          } else if (userRole === 'storeManager') {
            this.$router.push('/storeManagerHome');
          } else if (userRole === 'user') {
            this.$router.push('/userHome');
          }else {
            console.error('Unknown user role');
            this.$router.push('/unauthorized');
          }
        }
      } catch (error) {
        console.error('Error decoding token:', error);
        localStorage.removeItem('jwtToken');
        this.$router.push('/login');
      }
    }
  },
};
</script>
<style scoped>
.main-content {
  background-color: rgb(250, 220, 139);
}
.center-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 50px); /* Subtract the navbar height */
}

.login-box {
  width: 300px;
  padding: 20px;
  border: 1px solid #ccc;
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.login-box h2 {
  text-align: center;
  margin-bottom: 20px;
}

.login-box label {
  display: block;
  margin-bottom: 8px;
}

.login-box input {
  width: 100%;
  padding: 8px;
  margin-bottom: 16px;
  box-sizing: border-box;
}

.login-box button {
  background-color: #3498db;
  color: #fff;
  padding: 10px;
  border: none;
  width: 100%;
  cursor: pointer;
}

.login-box button:hover {
  background-color: #2980b9;
}
</style>
