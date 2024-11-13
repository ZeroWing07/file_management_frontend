import React, { useRef, useState, forwardRef, useImperativeHandle } from 'react';

const CanvasComponent = forwardRef(({ width, height }, ref) => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);

  const startDrawing = (e) => {
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    context.strokeStyle = '#000';
    context.lineWidth = 3;
    context.beginPath();
    context.moveTo(e.nativeEvent.offsetX, e.nativeEvent.offsetY);
    setIsDrawing(true);
  };

  const draw = (e) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    context.lineTo(e.nativeEvent.offsetX, e.nativeEvent.offsetY);
    context.stroke();
  };

  const stopDrawing = () => setIsDrawing(false);

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
  };

  // Expose the canvas data URL method to parent component via ref
  useImperativeHandle(ref, () => ({
    toDataURL: () => canvasRef.current.toDataURL(),
  }));

  return (
    <div>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{ border: '1px solid black' }}
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseLeave={stopDrawing}
      />
      <button onClick={clearCanvas}>Clear Canvas</button>
    </div>
  );
});

export default CanvasComponent;