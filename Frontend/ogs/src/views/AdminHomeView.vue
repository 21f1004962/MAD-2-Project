<template>
  <div>
    <NavbarVue>
      <div>
        <a
          href="/adminRequests"
          class="nav-item nav-link"
          style="display: inline; color: black"
        >Requests</a>
        <LogoutButtonVue />
      </div>
    </NavbarVue>
    <MessagesVue :messages="messages" />
    <CategoryForm
      :showModal="showCategoryForm"
      :editingCategory="editingCategory"
      :categoryId="editingCategoryId"
      :categoryNameProp="editingCategoryName"
      @close="closeCategoryForm"
      @category-updated="handleCategoryUpdated"
      @category-added="handleCategoryAdded"
    />
    <div class="main-content">
      <div class="container mt-5">
        <div
          v-if="categories === null"
          class="container-sm mt-5"
          style="max-width: 800px; margin: 0 auto; padding: 20px"
        >
          <h2>No category or products created.</h2>
          <br /><br /><br />
          <button
            class="btn btn-dark"
            @click.prevent="navigateToAddCategory"
          >Click here to add</button>
        </div>
        <div v-else>
          <h2 style="margin-top: 40px">Categories</h2>
          <div class="row">
            <div
              v-for="(category, categoryId) in categories"
              :key="categoryId"
              class="col-md-3 mb-4"
            >
              <div class="card text-center">
                <div class="card-header"></div>
                <div class="card-body">
                  <h5 class="card-title">{{ category }}</h5>
                  <button
                    class="btn btn-warning"
                    @click.prevent="navigateToEditCategory(categoryId)"
                  >Edit</button>
                  <br /><br />
                  <button
                    class="btn btn-danger"
                    @click.prevent="navigateToDeleteCategory(categoryId)"
                  >Delete</button>
                </div>
                <div class="card-footer text-muted"></div>
              </div>
            </div>
          </div>
          <div>
            <button
              id="cat"
              class="btn btn-secondary mx-3"
              style="position: fixed; bottom: 30px; right: 0"
              @click.prevent="navigateToAddCategory"
            >+</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LogoutButtonVue from "../components/LogoutButton.vue";
import NavbarVue from "../components/Navbar.vue";
import axios from "axios";
import MessagesVue from "../components/Messages.vue";
import CategoryForm from "../components/CategoryForm.vue";

export default {
  name: "AdminHomeView",
  data() {
    return {
      categories: [],
      showCategoryForm: false,
      editingCategory: false,
      editingCategoryId: null,
      editingCategoryName: null,
      messages: [],
    };
  },
  components: {
    NavbarVue,
    LogoutButtonVue,
    MessagesVue,
    CategoryForm,
  },
  beforeCreate() {
    const jwtToken = localStorage.getItem("jwtToken");

    axios
      .get("http://127.0.0.1:5000/getCategories", {
        headers: { "x-access-token": jwtToken },
      })
      .then((response) => {
        this.categories = response.data.categories;
      })
      .catch((error) => {
        console.error("Error fetching categories:", error);
      });
  },
  methods: {
    showMessage(message) {
      this.messages.push(message);

      setTimeout(() => {
        this.messages.shift();
      }, 5000);
    },
    navigateToAddCategory() {
      this.editingCategory = false;
      this.showCategoryForm = true;
    },
    navigateToEditCategory(categoryId) {
      this.editingCategory = true;
      this.editingCategoryId = parseInt(categoryId);
      this.editingCategoryName = this.categories[categoryId];
      this.showCategoryForm = true;
    },
    navigateToDeleteCategory(categoryId) {
      const jwtToken = localStorage.getItem("jwtToken");

      const formData = new FormData();
      formData.append('categoryid', categoryId);

      axios
        .delete("http://127.0.0.1:5000/adminDeleteCategory", {
          headers: {
            "x-access-token": jwtToken,
          },
          data: formData,
        })
        .then((response) => {
          this.showMessage({
            type: "success",
            text: response.data,
          });
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        })
        .catch((error) => {
          console.error("Error deleting category:", error);
          this.showMessage({
            type: "failure",
            text: "Failed to delete category. Please try again later.",
          });
        });
    },


    closeCategoryForm() {
      this.showCategoryForm = false;
    },
    handleCategoryUpdated(message) {
      this.showMessage(message);
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    },

    handleCategoryAdded(message) {
      this.showMessage(message);
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    },
  },
};
</script>

<style scoped>
.card {
  margin-bottom: 20px;
  height: 100%;
}

.card-header {
  background-color: #f5deb3;
  text-align: center;
  font-weight: bold;
}

.card-container {
  background-color: lightgreen;
  padding: 20px;
  margin-top: 20px;
  max-height: 250px;
  overflow-y: scroll;
  margin-bottom: 40px;
}

.card-footer {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
}

.action-buttons {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
}

.accept-button,
.reject-button {
  padding: 8px 16px;
  cursor: pointer;
  border: none;
  border-radius: 4px;
  color: #fff;
  font-weight: bold;
}

.accept-button {
  background-color: #4caf50;
}

.reject-button {
  background-color: #f44336;
}
</style>
