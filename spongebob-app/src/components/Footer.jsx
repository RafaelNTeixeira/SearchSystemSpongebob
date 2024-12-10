import spongebob from "@/app/assets/spongebob.png"
import spongebobSquare from "@/app/assets/spongebob-square.jpg"
import Image from "next/image"

export function Footer() {
    return (
        <footer className="p-2 mt-10 bg-cyan-800 text-white">
            <div className="mx-10 flex md:flex-row flex-col justify-between items-center">
                <Image src={spongebob} alt="SpongeBob" width={100} height={100} />
                <div>
                    <div className="flex justify-center items-center gap-2">
                        <Image src={spongebobSquare} alt="SpongeBob" width={30} height={30} />
                        <p className="text-lg text-center font-semibold">© 2024 <span className="text-yellow-300">SpongeSearch</span></p>
                    </div>
                    <p className="text-lg font-semibold pl-3">Made with <span className="text-yellow-300">&#9829;</span> by T06G01</p>
                </div>
                <div className="text-center">
                    <p className="text-lg font-semibold">Authors:</p>
                    <p className="text-lg text-yellow-300 font-semibold">Carolina Gonçalves, José Isidro</p>
                    <p className="text-lg text-yellow-300 font-semibold">Marco Costa, Rafael Teixeira</p>
                </div>
            </div>
        </footer>
    )
}





