<template>
  <button @click="logout" class="nav-item btn btn-outline-danger" type="button">Logout</button>
</template>

<script>
export default {
  name: "LogoutButtonVue",
  methods: {
    logout() {
      localStorage.removeItem("jwtToken");
      this.$router.push("/");
    },
  },
};
</script>
