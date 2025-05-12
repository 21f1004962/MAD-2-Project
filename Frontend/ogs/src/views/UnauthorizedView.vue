<template>
  <div>
    <NavbarVue>
      <div>
        <a
          href="/login"
          class="nav-item nav-link"
          style="display: inline; color: black"
          >Home</a
        >
        <LogoutButtonVue />
      </div>
    </NavbarVue>
    <div class="main-content">
      <div class="unauthorized-container">
        <h1 class="text-danger">Unauthorized</h1>
      </div>
    </div>
  </div>
</template>

<script>
import LogoutButtonVue from "../components/LogoutButton.vue";
import NavbarVue from "../components/Navbar.vue";

export default {
  name: "UnauthorizedView",
  components: {
    NavbarVue,
    LogoutButtonVue,
  },
};
</script>

<style scoped>
.unauthorized-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh; /* Set the container height to fill the viewport */
}

.text-danger {
  color: red;
  font-size: 36px; /* Adjust the font size as needed */
  text-align: center;
}
</style>
