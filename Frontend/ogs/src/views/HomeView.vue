<template>
  <div>
    <NavbarVue />
    <div class="center-content">
      <p id="text1">GROCER EXPRESS</p>
      <p id="text2">Your grocery shopping made easy!</p>

      <div
        class="container d-flex justify-content-center"
        style="margin-top: 30px"
      >
        <a href="/login" class="btn btn-light ms-4" role="button"
          >Login</a
        >
        <a href="/register" class="btn btn-light ms-4" role="button">Register</a>
      </div>
    </div>
  </div>
</template>

<script>
import NavbarVue from "../components/Navbar.vue";

export default {
  name: "HomeView",
  components: {
    NavbarVue
  },
};
</script>

<style scoped>

#text1 {
  align-items: center;
  font-size: 5rem;
  color: rgb(7, 2, 2);
  text-align: center;
  text-shadow: 2px 2px 4px white;
}

#text2 {
  font-size: 2rem;
  color: rgb(5, 3, 3);
  text-align: center;
  padding-top: 20px;
}

button {
  padding-bottom: 10px;
}

.center-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 50px); /* Subtract the navbar height */
}
</style>
