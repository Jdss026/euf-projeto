import "./globals.css";
// O caminho correto é next/font/google
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Simulado EUF 2023.2",
  description: "Preparatório para o Exame Unificado de Física",
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-br">
      <body className={`${inter.className} bg-slate-50 antialiased`}>
        {children}
      </body>
    </html>
  );
}