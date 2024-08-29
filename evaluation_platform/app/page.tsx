"use client";

import Image from "next/image";
import React, { useEffect, useState } from 'react';
import Slider from '@/components/Slider';
import { redirect } from 'next/navigation'
import { getSetNumber, signout, submitData } from "./actions";

export default function Home() {

  const [setNumber, setSetNumber] = useState(1); // Default to 1 or any other placeholder value

  const [indications, setIndications] = useState({
    indication1: {
      comprehensiveness: 5,
      factuality: 5,
      conciseness: 5,
      text: ""
    },
    indication2: {
      comprehensiveness: 5,
      factuality: 5,
      conciseness: 5,
      text: ""
    },
    indication3: {
      comprehensiveness: 5,
      factuality: 5,
      conciseness: 5,
      text: ""
    },
  });

  const [notes, setNotes] = useState({
    note1: {title: "", text: ""},
    note2: {title: "", text: ""},
    note3: {title: "", text: ""},
    note4: {title: "", text: ""},
    note5: {title: "", text: ""},
    note6: {title: "", text: ""},
    note7: {title: "", text: ""},
    note8: {title: "", text: ""},
    note9: {title: "", text: ""},
    note10: {title: "", text: ""}
  })

  const [comments, setComments] = useState({
    indication1: '',
    indication2: '',
    indication3: '',
  });

  const handleSliderChange = (indication: keyof typeof indications, metric: string, value: number) => {
    setIndications((prev) => ({
      ...prev,
      [indication]: {
        ...prev[indication],
        [metric]: value,
      },
    }));
  };

  const handleCommentChange = (indication: keyof typeof comments, value: string) => {
    setComments((prev) => ({
      ...prev,
      [indication]: value,
    }));
  };

  useEffect(() => {
    // Fetch the set number when the component mounts
    const fetchSetNumber = async () => {
      const number = await getSetNumber();
      setSetNumber(number);
    };

    const fetchIndicationText = async () => {
      const baseUrl = process.env.NODE_ENV === 'production' ? 'https://your-deployment-url.com' : 'http://localhost:3000';

      try {
        const responses = await Promise.all([
          fetch(`${baseUrl}/set${setNumber}/indication1.txt`).then(res => res.text()),
          fetch(`${baseUrl}/set${setNumber}/indication2.txt`).then(res => res.text()),
          fetch(`${baseUrl}/set${setNumber}/indication3.txt`).then(res => res.text()),
        ]);

        setIndications(prev => ({
          ...prev,
          indication1: { ...prev.indication1, text: responses[0] },
          indication2: { ...prev.indication2, text: responses[1] },
          indication3: { ...prev.indication3, text: responses[2] },
        }));
      } catch (error) {
        console.error('Error fetching indication text files:', error);
      }
    };
    const fetchNoteText = async () => {
      const baseUrl = process.env.NODE_ENV === 'production' ? 'https://your-deployment-url.com' : 'http://localhost:3000';
    
      try {
        const responses = await Promise.all([
          fetch(`${baseUrl}/set${setNumber}/note1.txt`).then(res => res.text()),
          fetch(`${baseUrl}/set${setNumber}/note2.txt`).then(res => res.text()),
          fetch(`${baseUrl}/set${setNumber}/note3.txt`).then(res => res.text()),
          fetch(`${baseUrl}/set${setNumber}/note4.txt`).then(res => res.text()),
          fetch(`${baseUrl}/set${setNumber}/note5.txt`).then(res => res.text()),
          fetch(`${baseUrl}/set${setNumber}/note6.txt`).then(res => res.text()),
          fetch(`${baseUrl}/set${setNumber}/note7.txt`).then(res => res.text()),
          fetch(`${baseUrl}/set${setNumber}/note8.txt`).then(res => res.text()),
          fetch(`${baseUrl}/set${setNumber}/note9.txt`).then(res => res.text()),
          fetch(`${baseUrl}/set${setNumber}/note10.txt`).then(res => res.text()),
        ]);
    
        const parsedNotes = responses.map(text => {
          const [title, ...body] = text.split('\n');
          return { title, text: body.join('\n') };
        });
    
        setNotes({
          note1: parsedNotes[0],
          note2: parsedNotes[1],
          note3: parsedNotes[2],
          note4: parsedNotes[3],
          note5: parsedNotes[4],
          note6: parsedNotes[5],
          note7: parsedNotes[6],
          note8: parsedNotes[7],
          note9: parsedNotes[8],
          note10: parsedNotes[9],
        });
      } catch (error) {
        console.error('Error fetching note text files:', error);
      }
    };

    fetchSetNumber();
    fetchIndicationText();
    fetchNoteText()
  }, [setNumber]);

  const handleSignout = async () => {
    await signout();
  };

  const handleSubmitData = async () => {
    await submitData(
      indications.indication1.comprehensiveness,
      indications.indication2.comprehensiveness,
      indications.indication3.comprehensiveness,
      indications.indication1.factuality,
      indications.indication2.factuality,
      indications.indication3.factuality,
      indications.indication1.conciseness,
      indications.indication2.conciseness,
      indications.indication3.conciseness,
      comments.indication1,
      comments.indication2,
      comments.indication3,
      setNumber
    );

    // setIndications({
    //   indication1: {
    //     comprehensiveness: 5,
    //     factuality: 5,
    //     conciseness: 5,
    //   },
    //   indication2: {
    //     comprehensiveness: 5,
    //     factuality: 5,
    //     conciseness: 5,
    //   },
    //   indication3: {
    //     comprehensiveness: 5,
    //     factuality: 5,
    //     conciseness: 5,
    //   },
    // });

    // setComments({
    //   indication1: '',
    //   indication2: '',
    //   indication3: '',
    // });

    setSetNumber((prev) => prev + 1)
    window.scrollTo({ top: 0})
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-5">
      
      <div className="w-full max-w-8xl bg-white shadow-lg rounded-lg p-8 flex flex-col">

      <div className="flex justify-between items-center mb-10">
      <h2 className="bg-blue-600 px-4 py-2 rounded-lg text-white">Case {setNumber} out of 100</h2>
      <button
          onClick={handleSignout}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Sign Out
        </button>
      </div>

      <div className="flex flex-row">
        <div className="w-3/4 pr-4">
          <h2 className="text-xl font-semibold mb-4">Notes</h2>
          <div className="space-y-4">
          {Object.keys(notes).map((noteKey) => {
      const key = noteKey as keyof typeof notes; // Type assertion
      return (
        <details key={key} className="bg-gray-100 p-4 rounded-lg">
          <summary className="cursor-pointer text-lg font-medium">
            {notes[key].title}
          </summary>
          <p className="mt-2 text-sm text-gray-600 h-40 overflow-y-auto">
            {notes[key].text}
          </p>
        </details>
      );
    })}


        </div>
        </div>
        <div className="w-1/4 pl-4">
          <h2 className="text-xl font-semibold mb-4">Evaluation</h2>
          <div className="bg-gray-100 p-4 rounded-lg space-y-6">
            {/* Indication #1 */}
            <div>
              <h3 className="text-lg font-medium">Indication #1</h3>
              <h4 className="text-md font-normal">{indications.indication1.text}</h4>
              <br/>
              <Slider
                label="Comprehensiveness (i.e. Does it omit any radiologically relevant and/or important detail?)"
                value={indications.indication1.comprehensiveness}
                onChange={(value) => handleSliderChange('indication1', 'comprehensiveness', value)}
              />
              <Slider
                label="Factuality (i.e. Does it make up or hallucinate any false information that was not in the medical record?)"
                value={indications.indication1.factuality}
                onChange={(value) => handleSliderChange('indication1', 'factuality', value)}
              />
              <Slider
                label="Conciseness (i.e. Could the information be said in shorter /simpler phrases or sentences or do they ramble on with excessive words?)"
                value={indications.indication1.conciseness}
                onChange={(value) => handleSliderChange('indication1', 'conciseness', value)}
              />
              <h2>Comment (Optional)</h2>
              <textarea
                className="mt-2 w-full p-2 border border-gray-300 rounded-lg"
                value={comments.indication1}
                onChange={(e) => handleCommentChange('indication1', e.target.value)}
              />
            </div>

            {/* Indication #2 */}
            <div>
            <h3 className="text-lg font-medium">Indication #2</h3>
            <h4 className="text-md font-normal">{indications.indication2.text}</h4>
            <br/>
              <Slider
                label="Comprehensiveness (i.e. Does it omit any radiologically relevant and/or important detail?)"
                value={indications.indication2.comprehensiveness}
                onChange={(value) => handleSliderChange('indication2', 'comprehensiveness', value)}
              />
              <Slider
                label="Factuality (i.e. Does it make up or hallucinate any false information that was not in the medical record?)"
                value={indications.indication2.factuality}
                onChange={(value) => handleSliderChange('indication2', 'factuality', value)}
              />
              <Slider
                label="Conciseness (i.e. Could the information be said in shorter /simpler phrases or sentences or do they ramble on with excessive words?)"
                value={indications.indication2.conciseness}
                onChange={(value) => handleSliderChange('indication2', 'conciseness', value)}
              />
              <h2>Comment (Optional)</h2>
              <textarea
                className="mt-2 w-full p-2 border border-gray-300 rounded-lg"
                value={comments.indication2}
                onChange={(e) => handleCommentChange('indication2', e.target.value)}
              />
            </div>

            {/* Indication #3 */}
            <div>
            <h3 className="text-lg font-medium">Indication #3</h3>
            <h4 className="text-md font-normal">{indications.indication3.text}</h4>
            <br/>
              <Slider
                label="Comprehensiveness (i.e. Does it omit any radiologically relevant and/or important detail?)"
                value={indications.indication3.comprehensiveness}
                onChange={(value) => handleSliderChange('indication3', 'comprehensiveness', value)}
              />
              <Slider
                label="Factuality (i.e. Does it make up or hallucinate any false information that was not in the medical record?)"
                value={indications.indication3.factuality}
                onChange={(value) => handleSliderChange('indication3', 'factuality', value)}
              />
              <Slider
                label="Conciseness (i.e. Could the information be said in shorter /simpler phrases or sentences or do they ramble on with excessive words?)"
                value={indications.indication3.conciseness}
                onChange={(value) => handleSliderChange('indication3', 'conciseness', value)}
              />
              <h2>Comment (Optional)</h2>
              <textarea
                className="mt-2 w-full p-2 border border-gray-300 rounded-lg"
                value={comments.indication3}
                onChange={(e) => handleCommentChange('indication3', e.target.value)}
              />
            </div>



            {/* Centered and Black Submit Button */}
            <div className="flex justify-center">
              <button onClick={handleSubmitData} className="px-4 py-2 bg-blue-700 text-white rounded-lg">
                Submit Evaluation
              </button>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  );
}
