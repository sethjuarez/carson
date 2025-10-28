import React, { useEffect, useState } from "react";
import styles from "./setting.module.scss";
import Tool from "../structure/tool";
import clsx from "clsx";
import Modal from "../structure/modal";

interface Props {
  id: string;
  icon: React.ReactNode;
  title: string;
  children?: React.ReactNode;
  className?: string;
}

const Setting: React.FC<Props> = ({
  id,
  icon,
  title,
  children,
  className,
}: Props) => {
  const [isOpen, setIsOpen] = useState(false);
  const toggleOpen = () => {
    setIsOpen((prev) => !prev);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest(`#${id}`)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("click", handleClickOutside);
    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <div id={id} className={styles.settings}>
      <Tool icon={icon} onClick={toggleOpen} title={title} />
      <Modal title={title} isOpen={isOpen} onClose={() => setIsOpen(false)}>
        {children}
      </Modal>
    </div>
  );
};

export default Setting;
