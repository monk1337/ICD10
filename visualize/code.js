import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { ChevronRight, ChevronDown, Plus, Minus } from 'lucide-react';

// Dummy data simulating ICD-10 code hierarchy
const dummyData = {
  code: "S52.112A",
  description: "Torus fracture of upper end of radius",
  type: "subcategory",
  children: ["S52.112B", "S52.112C"],
  excludes1: [
    "fracture of shaft of radius (S52.3-)",
    "fracture at wrist and hand level (S62.-)"
  ],
  excludes2: [
    "physeal fractures of upper end of radius (S59.2-)"
  ],
  includes: [
    "Fracture of proximal end of radius"
  ],
  inclusionTerms: [
    "Colles' fracture",
    "Smith's fracture"
  ],
  sevenCharacterDefinitions: {
    "A": "initial encounter for closed fracture",
    "D": "subsequent encounter for fracture with routine healing",
    "G": "subsequent encounter for fracture with delayed healing",
    "K": "subsequent encounter for fracture with nonunion",
    "P": "subsequent encounter for fracture with malunion",
    "S": "sequela"
  },
  additionalCodes: {
    "use_additional_code": "external cause code (V00-Y99)",
    "code_first": "any associated spinal cord injury (S24.0-, S24.1-)"
  },
  parentChain: {
    "S52.11": {
      code: "S52.11",
      description: "Torus fracture of upper end of radius",
      type: "subcategory",
      children: ["S52.112A", "S52.112B", "S52.112C"],
      sevenCharacterDefinitions: {
        "A": "initial encounter for closed fracture",
        "D": "subsequent encounter for fracture with routine healing"
      }
    },
    "S52": {
      code: "S52",
      description: "Fracture of forearm",
      type: "category",
      children: ["S52.11", "S52.12", "S52.13"],
      excludes1: [
        "traumatic amputation of forearm (S58.-)"
      ]
    }
  }
};

const CodeVisualizer = () => {
  const [expandedNodes, setExpandedNodes] = useState(new Set([dummyData.code]));
  const [expandedDetails, setExpandedDetails] = useState(new Set([dummyData.code]));
  
  const toggleNode = (nodeCode) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeCode)) {
      newExpanded.delete(nodeCode);
    } else {
      newExpanded.add(nodeCode);
    }
    setExpandedNodes(newExpanded);
  };
  
  const toggleDetails = (nodeCode) => {
    const newExpanded = new Set(expandedDetails);
    if (newExpanded.has(nodeCode)) {
      newExpanded.delete(nodeCode);
    } else {
      newExpanded.add(nodeCode);
    }
    setExpandedDetails(newExpanded);
  };

  const CodeNode = ({ nodeData, depth = 0 }) => {
    const isExpanded = expandedNodes.has(nodeData.code);
    const isDetailsExpanded = expandedDetails.has(nodeData.code);

    return (
      <div className="ml-6">
        <div className="flex items-start gap-2">
          <button
            onClick={() => toggleNode(nodeData.code)}
            className="mt-1 p-1 hover:bg-gray-100 rounded transition-colors"
          >
            {nodeData.children?.length > 0 ? (
              isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />
            ) : (
              <div className="w-4" />
            )}
          </button>
          
          <div className="flex-1 border rounded-lg p-3 my-1 bg-white shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-blue-600">{nodeData.code}</span>
                  <span className="text-xs bg-gray-100 rounded px-2 py-0.5">{nodeData.type}</span>
                </div>
                <div className="text-gray-700 mt-1">{nodeData.description}</div>
              </div>
              
              <button
                onClick={() => toggleDetails(nodeData.code)}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
              >
                {isDetailsExpanded ? <Minus size={16} /> : <Plus size={16} />}
              </button>
            </div>

            {isDetailsExpanded && (
              <div className="mt-4 space-y-4 text-sm">
                {nodeData.excludes1 && (
                  <div>
                    <div className="font-semibold text-red-600">Excludes1:</div>
                    <ul className="list-disc ml-4">
                      {nodeData.excludes1.map((item, idx) => (
                        <li key={idx} className="text-gray-600">{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {nodeData.excludes2 && (
                  <div>
                    <div className="font-semibold text-orange-600">Excludes2:</div>
                    <ul className="list-disc ml-4">
                      {nodeData.excludes2.map((item, idx) => (
                        <li key={idx} className="text-gray-600">{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {nodeData.includes && (
                  <div>
                    <div className="font-semibold text-green-600">Includes:</div>
                    <ul className="list-disc ml-4">
                      {nodeData.includes.map((item, idx) => (
                        <li key={idx} className="text-gray-600">{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {nodeData.inclusionTerms && (
                  <div>
                    <div className="font-semibold text-blue-600">Inclusion Terms:</div>
                    <ul className="list-disc ml-4">
                      {nodeData.inclusionTerms.map((item, idx) => (
                        <li key={idx} className="text-gray-600">{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {nodeData.sevenCharacterDefinitions && (
                  <div>
                    <div className="font-semibold text-purple-600">7th Character Definitions:</div>
                    <div className="grid grid-cols-2 gap-2 ml-4">
                      {Object.entries(nodeData.sevenCharacterDefinitions).map(([char, def]) => (
                        <div key={char} className="flex gap-2">
                          <span className="font-medium">{char}:</span>
                          <span className="text-gray-600">{def}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {nodeData.additionalCodes && (
                  <div>
                    <div className="font-semibold text-teal-600">Additional Codes:</div>
                    <div className="ml-4">
                      {Object.entries(nodeData.additionalCodes).map(([type, code]) => (
                        <div key={type} className="text-gray-600">
                          <span className="font-medium">{type}:</span> {code}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {isExpanded && nodeData.parentChain && (
          <div className="border-l-2 border-gray-200">
            {Object.values(nodeData.parentChain).map((parent, index) => (
              <CodeNode
                key={parent.code}
                nodeData={parent}
                depth={depth + 1}
              />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <Card className="p-6 max-w-4xl mx-auto bg-gray-50">
      <h2 className="text-xl font-bold mb-4">ICD-10 Code Hierarchy</h2>
      <div className="overflow-x-auto">
        <CodeNode nodeData={dummyData} />
      </div>
    </Card>
  );
};

export default CodeVisualizer;
