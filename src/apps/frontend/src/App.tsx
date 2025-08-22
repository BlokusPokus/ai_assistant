import React from "react";
import { Button, Input, Card, Loading, Error } from "@/components/ui";

function App() {
  const [inputValue, setInputValue] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);

  const handleButtonClick = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 2000);
  };

  const handleRetry = () => {
    console.log("Retry clicked");
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 text-center mb-8">
            Personal Assistant TDAH - React Foundation
          </h1>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Button Component Demo */}
            <Card title="Button Components" padding="lg">
              <div className="space-y-4">
                <div className="space-y-2">
                  <h4 className="font-medium text-gray-700">Variants</h4>
                  <div className="flex flex-wrap gap-2">
                    <Button variant="primary">Primary</Button>
                    <Button variant="secondary">Secondary</Button>
                    <Button variant="outline">Outline</Button>
                    <Button variant="ghost">Ghost</Button>
                    <Button variant="destructive">Destructive</Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium text-gray-700">Sizes</h4>
                  <div className="flex flex-wrap gap-2">
                    <Button size="sm">Small</Button>
                    <Button size="md">Medium</Button>
                    <Button size="lg">Large</Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium text-gray-700">States</h4>
                  <div className="flex flex-wrap gap-2">
                    <Button disabled>Disabled</Button>
                    <Button loading={isLoading} onClick={handleButtonClick}>
                      {isLoading ? "Loading..." : "Click to Load"}
                    </Button>
                  </div>
                </div>
              </div>
            </Card>

            {/* Input Component Demo */}
            <Card title="Input Components" padding="lg">
              <div className="space-y-4">
                <Input
                  label="Email Address"
                  type="email"
                  placeholder="Enter your email"
                  value={inputValue}
                  onChange={setInputValue}
                  required
                />

                <Input
                  label="Password"
                  type="password"
                  placeholder="Enter your password"
                  required
                />

                <Input
                  label="Username"
                  placeholder="Enter username"
                  error="Username is already taken"
                />

                <Input
                  label="Disabled Input"
                  placeholder="This input is disabled"
                  disabled
                />
              </div>
            </Card>

            {/* Loading Component Demo */}
            <Card title="Loading States" padding="lg">
              <div className="space-y-6">
                <div className="text-center">
                  <h4 className="font-medium text-gray-700 mb-2">Small</h4>
                  <Loading size="sm" text="Loading..." />
                </div>

                <div className="text-center">
                  <h4 className="font-medium text-gray-700 mb-2">Medium</h4>
                  <Loading size="md" text="Processing..." />
                </div>

                <div className="text-center">
                  <h4 className="font-medium text-gray-700 mb-2">Large</h4>
                  <Loading size="lg" text="Please wait..." />
                </div>
              </div>
            </Card>

            {/* Error Component Demo */}
            <Card title="Error States" padding="lg">
              <div className="space-y-4">
                <Error
                  title="Connection Failed"
                  message="Unable to connect to the server. Please check your internet connection and try again."
                  onRetry={handleRetry}
                />

                <Error
                  title="Validation Error"
                  message="Please fill in all required fields before submitting the form."
                />
              </div>
            </Card>
          </div>

          {/* Project Info */}
          <Card title="Project Information" className="mt-8">
            <div className="space-y-2 text-sm text-gray-600">
              <p>
                <strong>Task:</strong> 038 - React Project Foundation Setup
              </p>
              <p>
                <strong>Phase:</strong> 2.4 - User Interface Development
              </p>
              <p>
                <strong>Status:</strong> ✅ Foundation Complete
              </p>
              <p>
                <strong>Next:</strong> Task 039 - Authentication UI
                Implementation
              </p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default App;
