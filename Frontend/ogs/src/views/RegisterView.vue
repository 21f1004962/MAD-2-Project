<template>
  <div class="main-content">
    <NavbarVue />
    <div class="center-content">
      <MessagesVue :messages="messages" />
      <div
        class="container d-flex justify-content-center"
        style="margin-top: 30px"
      >
        <div class="registration-box">
          <h2>Register</h2>
          <form @submit.prevent="handleRegistrationSubmit">
            <label for="username">Username:</label>
            <input
              type="text"
              id="username"
              name="username"
              v-model="username"
              required
            />

            <label for="email">Email:</label>
            <input
              type="email"
              id="email"
              name="email"
              v-model="email"
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

            <label for="role">Role:</label>
            <select id="role" name="role" v-model="role" required>
              <option value="storeManager">Store Manager</option>
              <option value="user">User</option>
            </select>

            <button>Register</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavbarVue from "../components/Navbar.vue";
import MessagesVue from "../components/Messages.vue";
import axios from "axios";

export default {
  name: "RegisterView",
  data() {
    return {
      username: "",
      email: "",
      password: "",
      role: "user",
      messages: [],
    };
  },
  components: {
    NavbarVue,
    MessagesVue,
  },
  methods: {
    handleRegistrationSubmit() {
      const formData = new FormData();
      formData.append("username", this.username);
      formData.append("email", this.email);
      formData.append("password", this.password);
      formData.append("role", this.role);

      axios
        .post("http://127.0.0.1:5000/register", formData)
        .then((response) => {
          if (response.status === 202) {
            this.showMessage({
              text: "User with this username or email already exists. Please login.",
              type: "information",
            });
          } else {
            this.username = "";
            this.email = "";
            this.password = "";
            this.role = "user";
            this.showMessage({
              text: "Registration successful. Redirecting to login...",
              type: "success",
            });
            setTimeout(() => {
              this.$router.push("/login");
            }, 3000);
          }
        })
        .catch((error) => {
          this.showMessage({ text: error.response.data, type: "failure" });
        });
    },
    showMessage(message) {
      this.messages.push(message);

      setTimeout(() => {
        this.messages.shift();
      }, 5000);
    },
  },
};
</script>

<style scoped>
.registration-box {
  width: 300px;
  padding: 20px;
  border: 1px solid #ccc;
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.registration-box h2 {
  text-align: center;
  margin-bottom: 20px;
}

.registration-box label {
  display: block;
  margin-bottom: 8px;
}

.registration-box input,
.registration-box select {
  width: 100%;
  padding: 8px;
  margin-bottom: 16px;
  box-sizing: border-box;
}

.registration-box button {
  background-color: #3498db;
  color: #fff;
  padding: 10px;
  border: none;
  width: 100%;
  cursor: pointer;
}

.registration-box button:hover {
  background-color: #2980b9;
}
</style>
