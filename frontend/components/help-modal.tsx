import React from 'react';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import MarkdownRenderer from './markdown-renderer';

interface HelpModalProps {
  markdownContent: string;
}

const HelpModal: React.FC<HelpModalProps> = ({ markdownContent }) => {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Help</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[800px]">
        <DialogHeader>
          <DialogTitle>PRD Template Format</DialogTitle>
        </DialogHeader>
        <div className="prose max-w-none">
          <MarkdownRenderer content={markdownContent} />
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default HelpModal;
