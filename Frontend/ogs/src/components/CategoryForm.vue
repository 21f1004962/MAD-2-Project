<template>
  <div>
    <div :style="{ display: showModal ? 'flex' : 'none' }" class="modal">
      <div class="modal-background" @click="closeModal"></div>
      <div class="modal-card">
        <header class="modal-card-head has-background-primary">
          <p class="modal-card-title has-text-white" style="display: inline">
            {{ editingCategory ? "Edit Category" : "Add Category" }}
          </p>
          <button class="delete" style="float: right" @click="closeModal">
            X
          </button>
        </header>
        <section class="modal-card-body">
          <form @submit.prevent="handleSubmit" class="category-form">
            <div class="field">
              <label class="label">Category Name</label>
              <div class="control">
                <input
                  v-model="categoryName"
                  class="input"
                  type="text"
                  :placeholder="
                    editingCategory
                      ? categoryNameProp
                      : 'Enter new category name'
                  "
                  required
                />
              </div>
            </div>
            <div class="field">
              <div class="control">
                <button type="submit" class="button is-primary">
                  {{ editingCategory ? "Save Changes" : "Add Category" }}
                </button>
              </div>
            </div>
          </form>
        </section>
      </div>
      <button
        class="modal-close is-large"
        aria-label="close"
        @click="closeModal"
      ></button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  props: {
    showModal: Boolean,
    editingCategory: Boolean,
    categoryId: Number,
    categoryNameProp: String,
  },
  data() {
    return {
      categoryName: this.editingCategory ? this.categoryNameProp : "",
    };
  },
  methods: {
    closeModal() {
      this.$emit("close");
    },
    handleSubmit() {
      const jwtToken = localStorage.getItem("jwtToken");
      let userRole = ""
      if (jwtToken) {
        const payload = jwtToken.split(".")[1];
        const decodedPayload = JSON.parse(atob(payload));
        userRole = decodedPayload.role;
      }
      if (userRole === "admin") {
        if (this.editingCategory) {
          const updatedCategory = new FormData();
          updatedCategory.append("categoryid", this.categoryId);
          updatedCategory.append("name", this.categoryName);

          axios
            .put("http://127.0.0.1:5000/adminEditCategory", updatedCategory, {
              headers: { "x-access-token": jwtToken },
            })
            .then(() => {
              this.$emit("category-updated", {
                type: "success",
                text: "Category updated successfully",
              });
              this.closeModal();
            })
            .catch((error) => {
              this.$emit("category-updated", {
                type: "failure",
                text: error.response.data,
              });
              this.closeModal();
            });
        } else {
          const newCategory = new FormData();
          newCategory.append("name", this.categoryName);

          axios
            .post("http://127.0.0.1:5000/adminAddCategory", newCategory, {
              headers: { "x-access-token": jwtToken },
            })
            .then(() => {
              this.$emit("category-added", {
                type: "success",
                text: "Category added successfully",
              });
              this.closeModal();
            })
            .catch((error) => {
              this.$emit("category-added", {
                type: "failure",
                text: error.response.data,
              });
              this.closeModal();
            });
        }
      } else if (userRole === "storeManager") {
        let requestedCategory = null;
        if (this.editingCategory) {
          requestedCategory = new FormData();
          requestedCategory.append("categoryid", this.categoryId);
          requestedCategory.append("operation", "Edit");
          requestedCategory.append("newName", this.categoryName);
        } else {
          requestedCategory = new FormData();
          requestedCategory.append("name", this.categoryName);
          requestedCategory.append("operation", "Add");
        }
        axios
          .post(
            "http://127.0.0.1:5000/storeManagerCategoryRequest",
            requestedCategory,
            {
              headers: { "x-access-token": jwtToken },
            }
          )
          .then(() => {
            this.$emit("category-added", {
              type: "success",
              text: "Category request added successfully",
            });
            this.closeModal();
          })
          .catch((error) => {
            this.$emit("category-added", {
              type: "failure",
              text: error.response.data,
            });
            this.closeModal();
          });
      } else {
        console.error("User does not have the required role for this action");
      }
    },
  },
};
</script>

<style scoped>
/* Add styles to position the modal */
.modal {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  justify-content: center;
  align-items: center;
}

.modal-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-card {
  position: absolute;
  z-index: 1;
  border: 1px solid #ccc;
  background-color: #fff;
  width: 400px; /* Adjust the width as needed */
}

.has-background-primary {
  background-color: #00d1b2;
}

/* Additional styles for the form container */
.modal-card-body {
  padding: 20px;
}

.category-form {
  padding: 20px;
}

.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: transparent;
  border: none;
  cursor: pointer;
}
</style>
