# KiteSurf Store — Kitesurfing Equipment E-commerce Website

**Project Status:** In Development

**Live Website:** To be added after deployment.

## Overview

KiteSurf Store is a planned full-stack e-commerce web application for customers in the United Kingdom who want to browse and purchase kitesurfing equipment online.

The website aims to provide a straightforward shopping experience, allowing customers to explore equipment categories, search and filter products, view detailed product information, manage a shopping cart and complete purchases securely.

Registered customers will be able to manage their personal information and view their previous orders.

The application will also provide authorised staff with a dedicated website interface for managing products, including creating, viewing, updating and removing products from the active catalogue.

KiteSurf Store is being developed as an original Django application for the **Gateway Qualifications Level 5 Diploma in Web Application Development — Unit 4: Full Stack Frameworks with Django (F/650/3528)**.

---

## Table of Contents

1. [Project Goals](#project-goals)
2. [Target Audience](#target-audience)
3. [User Stories and Prioritisation](#user-stories-and-prioritisation)
4. [Five Planes of UX](#five-planes-of-ux)

Additional sections will be added as the project develops.

---

## Project Goals

### Project Purpose

KiteSurf Store is a planned full-stack e-commerce website focused on selling kitesurfing equipment to customers in the United Kingdom.

The aim of the project is to create an accessible, responsive and user-friendly online store that makes it easy for customers to find suitable equipment and purchase it online.

The project will be developed as an original Django application for Unit 4: Full Stack Frameworks with Django.

### User Goals

- Browse kitesurfing equipment online.
- Find products through clear navigation and product categories.
- Search and filter products.
- Access detailed product information.
- Check product availability.
- Add products to a shopping cart.
- Manage shopping cart contents.
- Complete purchases securely.
- Receive clear feedback about their orders.
- Manage personal account information.
- View previous orders.
- Use the website on mobile, tablet and desktop devices.

### Site Owner Goals

- Present kitesurfing equipment through a professional online storefront.
- Organise products into relevant categories.
- Maintain accurate product information and prices.
- Manage products through a secure staff interface.
- Remove discontinued products from the active catalogue.
- Preserve historical order information.
- Keep reliable records of customer orders.
- Provide customers with a straightforward purchasing experience.

### Project Objectives

- Design an intuitive and responsive user interface.
- Develop an original full-stack application using Django.
- Design a relational database to support the store's functionality.
- Implement appropriate user authentication and access controls.
- Provide product management functionality.
- Integrate online payment processing.
- Apply testing throughout development.
- Deploy the completed application to a cloud hosting platform.

---

## Target Audience

KiteSurf Store is aimed at people in the United Kingdom who are interested in purchasing kitesurfing equipment online.

The website is designed with three main customer groups in mind.

### Beginner Kitesurfers

People who are new to kitesurfing and may need additional information before purchasing equipment.

Their main needs include:

- Clear product descriptions.
- Easy navigation between equipment categories.
- Visible prices and product availability.
- A straightforward purchasing process.

### Experienced Kitesurfers

Customers who already understand their equipment requirements and want to find suitable products efficiently.

Their main needs include:

- Quick access to specific equipment.
- Product search and filtering.
- Detailed product specifications.
- An efficient checkout process.

### Returning Customers

Customers who have previously purchased equipment and may want to shop again.

Their main needs include:

- Convenient access to their accounts.
- Easy management of personal information.
- Access to previous orders.
- A consistent shopping experience.

### Business Users

The website will also serve authorised store staff responsible for maintaining the online catalogue.

Their main needs include:

- Managing product information and prices.
- Adding new products.
- Updating existing products.
- Removing products that are no longer offered.
- Maintaining accurate product availability.

### Design Considerations

The needs of these user groups will guide the website's design and development.

The interface will aim to provide clear navigation, readable content, accessible controls and responsive layouts across different screen sizes.

---

## User Stories and Prioritisation

User stories define the planned functionality of KiteSurf Store from the perspective of visitors, registered customers and store staff.

The requirements are prioritised using the MoSCoW method:

- **Must Have:** Essential functionality required for the application.
- **Should Have:** Important improvements that support the user experience.
- **Could Have:** Optional features that may be implemented if time allows.
- **Won't Have:** Features excluded from the current project scope.

### Must Have

| ID | User Story |
|---|---|
| US01 | As a visitor, I want to browse products so that I can explore the available kitesurfing equipment. |
| US02 | As a visitor, I want to view product details so that I can make informed purchasing decisions. |
| US03 | As a customer, I want to add products to a shopping cart so that I can purchase multiple items together. |
| US04 | As a customer, I want to update quantities and remove products from my cart so that I can control my order. |
| US05 | As a customer, I want to see my order total so that I know how much I will pay. |
| US06 | As a customer, I want to complete a secure online payment so that I can purchase equipment. |
| US07 | As a customer, I want to receive confirmation of successful or unsuccessful payments so that I know the status of my purchase. |
| US08 | As a visitor, I want to register an account so that I can access customer-specific features. |
| US09 | As a registered customer, I want to log in and log out securely so that I can protect my account. |
| US10 | As a registered customer, I want to manage my personal information so that my account details remain accurate. |
| US11 | As a registered customer, I want to view my previous orders so that I can keep track of my purchases. |
| US12 | As a store administrator, I want to add products through the website so that I can expand the catalogue. |
| US13 | As a store administrator, I want to view and edit product information so that I can maintain accurate listings. |
| US14 | As a store administrator, I want to remove products from the active catalogue so that discontinued equipment is no longer available for purchase while existing order records remain intact. |
| US15 | As a store administrator, I want product management restricted to authorised staff so that customer accounts cannot modify the catalogue. |
| US16 | As a user, I want clear validation messages so that I can correct invalid information. |
| US17 | As a user, I want the website to work on different screen sizes so that I can shop using my preferred device. |
| US18 | As a visitor, I want to search for products by name so that I can find specific equipment quickly. |
| US19 | As a visitor, I want to filter products by category so that I can narrow down the catalogue. |
| US20 | As a customer, I want to see product availability so that I know whether an item can be purchased. |
| US21 | As a customer, I want my shopping cart to persist while browsing so that I do not lose selected products. |
| US24 | As a visitor, I want registration and login pages to be available only when I am logged out so that the authentication process is clear and appropriate to my current session. |
| US25 | As a customer, I want my personal information and order history to be accessible only to me so that other customers cannot view my private data. |

### Should Have

No features are currently assigned to this priority. The initial development plan focuses on essential requirements before optional improvements.

### Could Have

| ID | User Story |
|---|---|
| US22 | As a visitor, I want to sort products by price so that I can compare equipment within my budget. |
| US23 | As a customer, I want to see related products so that I can discover additional equipment. |

### Won't Have

The following features are excluded from the initial project scope:

- Product reviews and ratings.
- Customer wishlists.
- Discount codes and loyalty programmes.
- Multiple currencies.
- Advanced inventory management.
- Shipping carrier API integrations.

These features may be considered for future development.

### Development Tracking

Each user story will be linked to a GitHub Issue containing its acceptance criteria and implementation tasks.

Development progress will be documented through Git commits, automated tests and manual testing.

The implementation will prioritise Must Have requirements before optional functionality.

---

## Five Planes of UX

The UX planning for KiteSurf Store follows Jesse James Garrett's Five Planes of User Experience framework.

### 1. Strategy

The purpose of KiteSurf Store is to provide an online shopping experience for customers interested in kitesurfing equipment in the United Kingdom.

The website aims to help customers find suitable equipment, understand product specifications and complete purchases through a straightforward shopping process.

The main business objective is to provide an online storefront where authorised staff can maintain the product catalogue while preserving reliable customer order records.

The target audience and their needs are described in the [Target Audience](#target-audience) section.

### 2. Scope

The planned functionality is based on the requirements defined in the [User Stories and Prioritisation](#user-stories-and-prioritisation) section.

The essential functional requirements include:

- Product catalogue and individual product pages.
- Product search and category filtering.
- Product availability information.
- Shopping cart management.
- Customer registration and authentication.
- Customer profile management.
- Secure online checkout.
- Payment confirmation and error feedback.
- Customer order history.
- Staff-only product management.

The order of features listed above reflects the customer shopping experience rather than development priority.

Implementation priorities are defined in the User Stories and Prioritisation section.

Optional features, including price sorting and related products, will only be considered after essential functionality has been completed.

### 3. Structure

The planned information architecture is organised around the main customer shopping journey.

#### Customer Journey

1. Visit the homepage.
2. Browse, search or filter products.
3. Open a product details page.
4. Check product information and availability.
5. Add products to the shopping cart.
6. Review and update the cart.
7. Proceed to checkout.
8. Complete payment.
9. Receive payment confirmation.

#### Registered Customer Journey

Registered customers will also be able to:

1. Register or log in.
2. Access their account.
3. View and update personal information.
4. View previous orders.
5. Log out securely.

#### Staff Journey

Authorised staff will be able to:

1. Log in using an authorised account.
2. Access the product management interface.
3. View existing product records.
4. Add new products.
5. Edit product information.
6. Remove discontinued products from the active catalogue.

The final navigation structure and URL organisation will be documented as the application's pages are developed.

### 4. Skeleton

The interface will be designed to support clear navigation, readable product information and straightforward user interactions.

The initial layout requirements include:

- A consistent navigation bar.
- Clearly organised product listings.
- Product cards displaying essential information.
- Dedicated product details pages.
- Accessible forms with clear labels.
- Visible validation messages.
- A shopping cart displaying quantities and totals.
- Clear checkout actions.
- Understandable payment feedback.
- Responsive layouts for mobile, tablet and desktop devices.

Desktop and mobile wireframes will be created to establish the layout of the main pages before implementation.

The wireframes and any subsequent design changes will be documented in this section.

### 5. Surface

The visual design will aim to reflect the outdoor and water sports market while maintaining a professional e-commerce appearance.

The planned visual direction includes:

- A clean and modern interface.
- Product photography as a prominent visual element.
- Consistent typography and spacing.
- Clear visual hierarchy.
- Accessible colour contrast.
- Recognisable buttons and interactive elements.
- Consistent styling across the website.

The final colour palette, typography and visual components will be documented once the design decisions have been made.