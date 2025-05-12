<template>
  <div>
    <Navbar>
      <div>
        <a
          href="/storeManagerHome"
          class="nav-item nav-link"
          style="display: inline; color: black"
          >Home</a
        >
        <LogoutButtonVue />
      </div>
    </Navbar>
    <MessagesVue :messages="messages" />
    <ProductForm
      :showModal="showProductForm"
      :editingProduct="editingProduct"
      :productId="editingProductId"
      :productNameProp="editingProductName"
      :quantityProp="editingProductQuantity"
      :rateProp="editingRateQuantity"
      :rateUnitsProp="editingRateunitsQuantity"
      :categoryIdProp="addingCategoryId"
      @close="closeProductForm"
      @product-updated="handleProductOperation"
      @product-added="handleProductOperation"
    />
    <div class="container mt-5 main-content">
      <h1 class="text-center">
        PRODUCTS - {{ category_name }} ({{ products.length }})
      </h1>
      <br />
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Sno</th>
            <th>Product</th>
            <th>Quantity</th>
            <th>Rate/Unit (in Rs)</th>
            <th>Unit</th>
            <th></th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.productid">
            <td>{{ product.sno }}</td>
            <td>{{ product.name }}</td>
            <td>{{ product.quantity }}</td>
            <td>{{ product.rate }}</td>
            <td>{{ product.rateunits }}</td>
            <td>
              <a
                @click="
                  editProduct(
                    product.productid,
                    product.name,
                    product.quantity,
                    product.rate,
                    product.rateunits
                  )
                "
                class="btn btn-info"
                >Edit</a
              >
            </td>
            <td>
              <a
                @click="deleteProduct(product.productid)"
                class="btn btn-danger"
                >Delete</a
              >
            </td>
          </tr>
        </tbody>

        <a
          @click="addProduct"
          class="btn btn-secondary mx-3"
          style="position: fixed; bottom: 30px; right: 20px"
          >+</a
        >
      </table>
    </div>
  </div>
</template>

<script>
import Navbar from "../components/Navbar.vue"; // Update the path accordingly
import MessagesVue from "../components/Messages.vue"; // Update the path accordingly
import axios from "axios";
import LogoutButtonVue from "../components/LogoutButton.vue";
import ProductForm from "../components/ProductForm.vue";

export default {
  name: "StoreManagerProductsView",
  data() {
    return {
      messages: [],
      products: [],
      showProductForm: false,
      editingProduct: false,
      editingProductId: null,
      editingProductName: "",
      editingProductQuantity: 0,
      editingProductRate: 0,
      editingProductRateunits: "kg",
      addingCategoryId: null,
    };
  },
  methods: {
    showMessage(message) {
      this.messages.push(message);

      setTimeout(() => {
        this.messages.shift();
      }, 5000);
    },
    editProduct(productId, name, quantity, rate, rateunits) {
      this.editingProduct = true;
      this.editingProductId = productId;
      this.editingProductName = name;
      this.editingProductQuantity = quantity;
      this.editingProductRate = rate;
      this.editingProductRateunits = rateunits;
      this.showProductForm = true;
    },
    addProduct() {
      this.editingProduct = false;
      this.addingCategoryId = this.categoryId;
      this.showProductForm = true;
    },
    deleteProduct(productid) {
      const jwtToken = localStorage.getItem("jwtToken");

      const formData = new FormData();
      formData.append("productid", productid);

      axios
        .delete("http://127.0.0.1:5000/storeManagerDeleteProduct", {
          headers: {
            "x-access-token": jwtToken,
          },
          data: formData,
        })
        .then(() => {
          // Handle successful deletion
          this.showMessage({
            text: "Product successfully deleted!",
            type: "success",
          });

          // Reload the page after 2 seconds
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        })
        .catch((error) => {
          // Handle error
          this.showMessage({
            text: `Error deleting product: ${error.response.data}`,
            type: "failure",
          });
        });
    },
    closeProductForm() {
      this.showProductForm = false;
      this.addingCategoryId = null;
    },
    handleProductOperation(responseMessage) {
      if (responseMessage.type === "success") {
        this.showMessage({
          text: responseMessage.text,
          type: "success",
        });
        setTimeout(() => {
          window.location.reload(); // Reload the page after 2 seconds
        }, 2000);
      } else {
        this.showMessage({
          text: responseMessage.text,
          type: "failure",
        });
      }
    },
  },
  components: {
    Navbar,
    MessagesVue,
    LogoutButtonVue,
    ProductForm,
  },
  beforeCreate() {
    this.categoryId = this.$route.params.CategoryId;

    const jwtToken = localStorage.getItem("jwtToken");

    // Make Axios GET request to fetch category name
    axios
      .get(
        `http://127.0.0.1:5000/getCategoryName?categoryId=${this.categoryId}`,
        {
          headers: { "x-access-token": jwtToken },
        }
      )
      .then((response) => {
        this.category_name = response.data.category_name;
      })
      .catch((error) => {
        this.showMessage({
          type: "failure",
          text: error.response.data``,
        });
      });

    axios
      .get(
        `http://127.0.0.1:5000/storeManagerGetProducts?categoryid=${this.categoryId}`,
        {
          headers: { "x-access-token": jwtToken },
        }
      )
      .then((response) => {
        // Update products with the fetched products list
        this.products = response.data;
      })
      .catch((error) => {
        this.showMessage({
          type: "failure",
          text: error.response.data,
        });
      });
  },
};
</script>

<style>
/* Add any custom styles if needed */
</style>
