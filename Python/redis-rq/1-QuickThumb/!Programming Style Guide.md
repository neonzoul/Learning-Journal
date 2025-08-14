### **Programming Style Guide for Python**

#### **Guiding Philosophy**

The goal is to write code that is clear, maintainable, and leverages modern Python features for type safety and reliability. The style is **declarative**, emphasizes **separation of concerns**, and values **readability over clever shortcuts**. The aim is to build robust, long-lasting applications.

#### **Key Principles**

1.  **Declarative & Data-Oriented:** I prefer to describe _what_ the code should accomplish, letting the framework handle the implementation details.

    -   [cite\_start]**Examples:** Using decorators in FastAPI to define API endpoints and using `SQLModel` to define the shape of database tables[cite: 5].

2.  **Strongly Typed & Type-Safe:** Code must use Python's `typing` module extensively to catch errors early and serve as self-documentation.

    -   **Usage:** Comprehensive use of `Type`, `Protocol`, `List`, `Dict`, `Any`, and Union types (`|`).
    -   **Goal:** Ensure clarity and prevent runtime type errors.

3.  **Clarity and Readability:** Code should be easy for another developer (or myself in 6 months) to understand. This means using clear, descriptive names for variables and functions and structuring code logically.

4.  **Modular & Decoupled (Separation of Concerns):** Different parts of the application must have distinct responsibilities.

    -   [cite\_start]**Example:** The project structure separates API endpoints, database models, business logic (the engine), and core configuration into different directories[cite: 5].

5.  **Behavior Defined by Interfaces (Protocols):** When defining objects with specific behaviors, their "contract" should be defined using `typing.Protocol`. This leads to more flexible, testable, and interchangeable components.

6.  **Use of Modern, Extensible Patterns:** The architecture should favor patterns that allow for future growth without major refactoring.

    -   [cite\_start]**Example:** The `AutomateOS` engine is built on a **Plugin Architecture** using dynamic loading (`importlib`) to ensure new nodes can be added easily[cite: 1]. The **Factory Pattern** is also a valued tool for creating configured, behavior-focused objects.

#### **Code Example Embodying These Principles**

This example demonstrates many of the principles above:

```python
from typing import Type, Protocol

# Principle 5: Behavior is defined by a clear Protocol.
class APIClientProtocol(Protocol):
    api_key: str
    endpoint: str

    # Principle 2: Strong type hints for all methods and parameters.
    def __init__(self, api_key: str) -> None: ...
    def get_full_url(self, endpoint: str) -> str: ...
    def display_config(self) -> None: ...

# Principle 6: Factory Pattern is used to create configured objects.
# Principle 2: The return type is clearly defined as a Type that adheres to the protocol.
def create_api_client(base_url: str) -> Type[APIClientProtocol]:

    # The class has clear, type-hinted attributes.
    class ClientApi:
        api_key: str
        endpoint: str

        def __init__(self, api_key: str) -> None:
            self.api_key = api_key
            self.endpoint = ""

        def get_full_url(self, endpoint: str) -> str:
            self.endpoint = f"{base_url}{endpoint}"
            return self.endpoint

        def display_config(self) -> None:
            print(f"Client configured for Base URL: {base_url} with API Key: {self.api_key}")

    return ClientApi
```
