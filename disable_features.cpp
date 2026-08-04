#include <windows.h>
#include <iostream>

void disableFeature(const char* featureName) {
    // Implement the logic to disable each feature here
    std::cout << "Disabling: " << featureName << std::endl;
}

int main() {
    int choice = 0;
    std::cout << "Choose which features to disable:\n";
    std::cout << "1. Copilot\n2. Cortana\n3. Defender\n4. Update\n5. All\n";
    std::cin >> choice;

    switch (choice) {
        case 1:
            disableFeature("Copilot");
            break;
        case 2:
            disableFeature("Cortana");
            break;
        case 3:
            disableFeature("Defender");
            break;
        case 4:
            disableFeature("Update");
            break;
        case 5:
            disableFeature("Copilot");
            disableFeature("Cortana");
            disableFeature("Defender");
            disableFeature("Update");
            break;
        default:
            std::cout << "Invalid choice.\n";
            return 1;
    }

    return 0;
}