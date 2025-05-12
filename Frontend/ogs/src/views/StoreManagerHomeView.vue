<template>
  <div>
    <Navbar>
      <div>
        <LogoutButtonVue />
      </div>
    </Navbar>
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
    <ProductForm
      :showModal="showProductForm"
      :categoryIdProp="selectedCategoryId"
      @close="closeProductForm"
      @product-added="handleProductAdded"
    />
    <div class="main-content" style="padding: 20px">
      <h2 style="margin-top: 40px">Categories</h2>
      <div class="container mt-5" v-if="categories === null">
        <div
          class="container-sm mt-5"
          style="max-width: 800px; margin: 0 auto; padding: 20px"
        >
          <h2>No category or products created.</h2>
          <br /><br /><br />
          <a href="/adminAddCategory" class="btn btn-dark">Click here to add</a>
        </div>
      </div>

      <div class="row" v-else>
        <div
          v-for="(category, categoryId) in categories"
          :key="categoryId"
          class="col-md-3 mb-4"
        >
          <div class="card text-center">
            <div class="card-header"></div>

            <div class="card-body">
              <h5 class="card-title">{{ category }}</h5>

              <a
                href="#"
                @click="addProducts(categoryId)"
                class="btn btn-success"
                >Add products</a
              >

              <br /><br />
              <a
                href="#"
                @click="editCategory(categoryId)"
                class="btn btn-warning mx-1"
                >Edit</a
              >

              <a
                href="#"
                @click="deleteCategory(categoryId)"
                class="btn btn-danger"
                >Delete</a
              >

              <br /><br />
              <a href="#" @click="showProducts(categoryId)" class="btn btn-info"
                >Show products</a
              >
            </div>

            <div class="card-footer text-muted"></div>
          </div>
        </div>
      </div>

      <div>
        <a
          href="#"
          @click="addCategory"
          id="cat"
          class="btn btn-secondary mx-3"
          style="position: fixed; bottom: 30px; right: 0"
          >+</a
        >
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from "../components/Navbar.vue";
import MessagesVue from "../components/Messages.vue";
import axios from "axios";
import LogoutButtonVue from "../components/LogoutButton.vue";
import CategoryForm from "../components/CategoryForm.vue";
import ProductForm from "../components/ProductForm.vue";

export default {
  name: "StoreManagerHomeView",
  components: {
    Navbar,
    MessagesVue,
    LogoutButtonVue,
    CategoryForm,
    ProductForm,
  },
  data() {
    return {
      messages: [],
      categories: null,
      showCategoryForm: false,
      editingCategory: false,
      editingCategoryId: null,
      editingCategoryName: null,
      showProductForm: false,
      selectedCategoryId: null,
    };
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
        this.showMessage({
            type: "failure",
            text: error.response.data,
          });
      });
  },
  methods: {
    showMessage(message) {
      this.messages.push(message);

      setTimeout(() => {
        this.messages.shift();
      }, 5000);
    },
    addCategory() {
      this.editingCategory = false;
      this.showCategoryForm = true;
    },
    addProducts(categoryId) {
      this.selectedCategoryId = parseInt(categoryId);
      this.showProductForm = true;
    },
    editCategory(categoryId) {
      this.editingCategory = true;
      this.editingCategoryId = parseInt(categoryId);
      this.editingCategoryName = this.categories[categoryId];
      this.showCategoryForm = true;
    },
    deleteCategory(categoryId) {
      const jwtToken = localStorage.getItem("jwtToken");

      const formData = new FormData();
      formData.append("categoryid", categoryId);
      formData.append("operation", "Delete");

      axios
        .post("http://127.0.0.1:5000/storeManagerCategoryRequest", formData, {
          headers: {
            "x-access-token": jwtToken,
          },
        })
        .then((response) => {
          this.showMessage({
            type: "success",
            text: response.data,
          });
        })
        .catch((error) => {
          this.showMessage({
            type: "failure",
            text: error.response.data,
          });
        });
    },
    showProducts(CategoryId) {
      this.$router.push({
        name: "storeManagerProducts",
        params: { CategoryId },
      });
    },
    closeCategoryForm() {
      this.showCategoryForm = false;
    },
    closeProductForm() {
      this.showProductForm = false;
      this.selectedCategoryId = null;
    },
    handleProductAdded(responseMessage) {
      if (responseMessage.type === "success") {
        this.showMessage({
          text: responseMessage.text,
          type: "success",
        });
      } else {
        this.showMessage({
          text: responseMessage.text,
          type: "failure",
        });
      }
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
/* Add your scoped styles here */
.main-content {
  background-color: rgb(250, 220, 139);
}

.container {
  margin-top: 30px;
}

.card {
  margin-bottom: 20px;
}

.btn-secondary {
  position: fixed;
  bottom: 30px;
  right: 0;
}
</style>
