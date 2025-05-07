import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const model = searchParams.get('model');
  const features = searchParams.get('features');

  try {
    const backendRes = await fetch(
      `http://localhost:8000/forecast/${model}?features=${features}`
    );
    const data = await backendRes.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch forecast data' }, { status: 500 });
  }
}